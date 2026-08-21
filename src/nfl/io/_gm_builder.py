import re
from collections.abc import Iterator

from ._gm_parser import parse_proto_file
from .message import Message
from .override import Action, AddTemplate, Condition, Override, Predicate, RemTemplate
from .template import Template


def build_game_master(
    game_master_stream: Iterator[str], overrides_stream: Iterator[str] | None
) -> dict[str, dict[str, Template]]:
    parsed_game_master = parse_proto_file(game_master_stream)
    parsed_overrides = parse_proto_file(overrides_stream or iter(()))

    data: dict[str, dict[str, Template]] = {}
    mapper: dict[str, str] = {}

    for template in parsed_game_master.get_object_list("template", Template):
        data.setdefault(template.key, {})[template.template_id] = template
        mapper[template.template_id] = template.key

    for override in parsed_overrides.get_object_list("override", Override.from_message):
        if len(override.target) < 2:
            target = ".".join(override.target)
            raise ValueError(
                f'Invalid override target "{target}": '
                f"must contain at least a root key and a target. "
                f"Expected format: [key, ...path, target]. "
                f"Note: the root key is not a valid target, use `<undefined>` instead."
                # TODO Implement <undefined>
            )
        key, *path, target = override.target
        for template_id in override.template_id:
            if template_id not in mapper:
                raise ValueError(f"Unknown template_id in override: {template_id}")
            template_key = mapper[template_id]
            template = data[template_key][template_id]
            if key != template.key:
                raise ValueError(
                    f"Template key mismatch for template_id={template_id}: "
                    f"override targets key={key}, but template has key={template.key}"
                )
            value = _find_value(template.value, path, override.predicate)
            if override.action_type is Action.DEL or override.action_type is Action.SET:
                value.delete(target)
            if override.action_type is Action.ADD or override.action_type is Action.SET:
                for val in override.value:
                    value.add(target, val)

    for rem_template in parsed_overrides.get_object_list(
        "rem_template", RemTemplate.from_message
    ):
        for template_id in rem_template.template_id:
            template_key = mapper.pop(template_id)
            del data[template_key][template_id]

    for add_template in parsed_overrides.get_object_list(
        "add_template", AddTemplate.from_message
    ):
        template_id, key = add_template.template_id, add_template.key
        message_core = Message()
        message_data = Message()
        message_core.add("template_id", template_id)
        message_core.add("data", message_data)
        message_data.add("template_id", template_id)
        for value in add_template.value:
            message_data.add(key, value)
        template = Template(message_core)
        data.setdefault(template.key, {})[template.template_id] = template
        mapper[template.template_id] = template.key

    return data


def _find_value(
    value: Message, path: list[str], pred: tuple[Predicate, ...]
) -> Message:
    for step in path:
        step_key, step_index, step_cond = _unfold_step(step)
        if step_index is None:
            value = value.get_message(step_key)
        elif step_cond:
            value = next(
                v
                for v in value.get_message_list(step_key)
                if _match_predicate(v, pred[step_index], pred)
            )
        else:
            value = value.get_message_list(step_key)[step_index]
    return value


def _unfold_step(key: str) -> tuple[str, int | None, bool]:
    if m := re.match(r"(\w+)\[(\d+)\]", key):
        return (m.group(1), int(m.group(2)), False)
    if m := re.match(r"(\w+)\((\d+)\)", key):
        return (m.group(1), int(m.group(2)), True)
    return (key, None, False)


def _match_predicate(
    value: Message, predicate: Predicate, pred: tuple[Predicate, ...]
) -> bool:
    return all(_match_condition(value, cond, pred) for cond in predicate.condition)


def _match_condition(
    value: Message, condition: Condition, pred: tuple[Predicate, ...]
) -> bool:
    *path, target = condition.target
    value = _find_value(value, path, pred)
    return value.get(target) == condition.value
