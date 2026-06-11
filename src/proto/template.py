from proto.message import Message


class Template:
    def __init__(self, msg: Message) -> None:
        self.template_id = msg.get_string("template_id")

        data_msg = msg.get_message("data")

        data_template_id = data_msg.get_string("template_id")

        if self.template_id != data_template_id:
            raise ValueError(
                f"Mismatch on template_id and data.template_id: "
                f"{self.template_id} and {data_template_id}"
            )

        keys = [k for k in data_msg.keys() if k != "template_id"]

        if len(keys) > 1:
            raise ValueError(
                f"Multiple keys in template data "
                f"for template_id = {data_template_id}"
            )

        if not keys:
            self.key = ""
            self.value = Message()
        else:
            self.key = keys[0]
            self.value = data_msg.get_message(self.key)

    def __str__(self) -> str:
        data = f"    {self.key}: {self.value.format_message('    ')}\n" if self.key else ""

        return (
            f"{{\n"
            f"  template_id: {self.template_id}\n"
            f"  data: {{\n"
            f"    template_id: {self.template_id}\n"
            f"{data}"
            f"  }}\n"
            f"}}"
        )
