from nfl.helpers import get_poke
from nfl.proto import FORM_SETTINGS, HoloPokemonForm
from nfl.service.common.data import EXTENDED, POKEMON
from nfl.utils import f64


def run():
    for fs in FORM_SETTINGS:
        for f in [HoloPokemonForm.FORM_UNSET] + [form.form for form in fs.forms]:
            p = get_poke(POKEMON, fs.pokemon, f)
            e = get_poke(EXTENDED, fs.pokemon, f)
            if not p:
                print(f"pokemon_settings: {fs.pokemon} / {f}")
                continue
            if not e:
                print(f"pokemon_extended_settings: {fs.pokemon} / {f}")
                continue
            s = e.size_settings
            if f64(p.height_std_dev) != f64(f64(p.pokedex_height_m) * 0.125):
                print(f"height_std_dev: {fs.pokemon} / {f}")
            if f64(p.weight_std_dev) != f64(f64(p.pokedex_weight_kg) * 0.125):
                print(f"weight_std_dev: {fs.pokemon} / {f}")
            if f64(s.xxs_lower_bound) != f64(f64(p.pokedex_height_m) * 0.49):
                print(f"xxs_lower_bound: {fs.pokemon} / {f}")
            if f64(s.xs_lower_bound) != f64(f64(p.pokedex_height_m) * 0.5):
                print(f"xs_lower_bound: {fs.pokemon} / {f}")
            if f64(s.m_lower_bound) != f64(f64(p.pokedex_height_m) * 0.75):
                print(f"m_lower_bound: {fs.pokemon} / {f}")
            if f64(s.m_upper_bound) != f64(f64(p.pokedex_height_m) * 1.25):
                print(f"m_upper_bound: {fs.pokemon} / {f}")
            if f64(s.xl_upper_bound) != f64(f64(p.pokedex_height_m) * 1.5):
                print(f"xl_upper_bound: {fs.pokemon} / {f}")
            if f64(s.xxl_upper_bound) not in [
                f64(f64(p.pokedex_height_m) * k) for k in [1.55, 1.75, 2.0]
            ]:
                print(f"xxl_upper_bound: {fs.pokemon} / {f}")
    for fs in FORM_SETTINGS:
        for f in [HoloPokemonForm.FORM_UNSET] + [form.form for form in fs.forms]:
            p = get_poke(POKEMON, fs.pokemon, f)
            e = get_poke(EXTENDED, fs.pokemon, f)
            if not p:
                print(f"pokemon_settings: {fs.pokemon} / {f}")
                continue
            if not e:
                print(f"pokemon_extended_settings: {fs.pokemon} / {f}")
                continue
            eteos = {teo.temp_evo_id: teo for teo in e.temp_evo_overrides}
            for teo in p.temp_evo_overrides:
                eteo = eteos.get(teo.temp_evo_id)
                if not eteo:
                    print(
                        f"pokemon_extended_settings: {fs.pokemon} / {f} / {teo.temp_evo_id}"
                    )
                    continue
                s = eteo.size_settings
                if f64(teo.average_height_m) != f64(p.pokedex_height_m):
                    print(f"height_std_dev: {fs.pokemon} / {f} / {teo.temp_evo_id}")
                if f64(teo.average_weight_kg) != f64(p.pokedex_weight_kg):
                    print(f"weight_std_dev: {fs.pokemon} / {f} / {teo.temp_evo_id}")
                if f64(s.xxs_lower_bound) != f64(f64(teo.average_height_m) * 0.49):
                    print(f"xxs_lower_bound: {fs.pokemon} / {f} / {teo.temp_evo_id}")
                if f64(s.xs_lower_bound) != f64(f64(teo.average_height_m) * 0.5):
                    print(f"xs_lower_bound: {fs.pokemon} / {f} / {teo.temp_evo_id}")
                if f64(s.m_lower_bound) != f64(f64(teo.average_height_m) * 0.75):
                    print(f"m_lower_bound: {fs.pokemon} / {f} / {teo.temp_evo_id}")
                if f64(s.m_upper_bound) != f64(f64(teo.average_height_m) * 1.25):
                    print(f"m_upper_bound: {fs.pokemon} / {f} / {teo.temp_evo_id}")
                if f64(s.xl_upper_bound) != f64(f64(teo.average_height_m) * 1.5):
                    print(f"xl_upper_bound: {fs.pokemon} / {f} / {teo.temp_evo_id}")
                if f64(s.xxl_upper_bound) not in [
                    f64(f64(teo.average_height_m) * k) for k in [1.55, 1.75, 2.0]
                ]:
                    print(f"xxl_upper_bound: {fs.pokemon} / {f} / {teo.temp_evo_id}")
