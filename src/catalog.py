from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

REST = ROOT / 'data' / 'restaurants.csv'
MENUS = ROOT / 'data' / 'menus.csv'


def restaurants():
    return pd.read_csv(REST)


def menus():
    return pd.read_csv(MENUS)


def menu_for(rid):
    m = menus()
    return m[m.Restaurant_ID == rid].copy()


def add_restaurant(name, rid, location, phone, email):
    r = restaurants()

    if rid in set(r.Restaurant_ID):
        raise ValueError('Restaurant ID already exists.')

    new = pd.DataFrame(
        [[rid, name, location, phone, email]],
        columns=r.columns
    )

    pd.concat([r, new], ignore_index=True).to_csv(REST, index=False)


def add_menu_item(
    rid,
    item_id,
    name,
    meal_type,
    category,
    serving_mass_g,
    emission_factor,
    quantity_unit='kg'
):
    m = menus()

    if item_id in set(m.Item_ID):
        raise ValueError('Item ID already exists.')

    # menus.csv contains Portions_Per_Person as an additional column.
    # New/unknown menu items use 1.0 as the neutral default.
    if 'Portions_Per_Person' in m.columns:
        new = pd.DataFrame(
            [[
                rid,
                item_id,
                name,
                meal_type,
                category,
                serving_mass_g,
                emission_factor,
                quantity_unit,
                1.0
            ]],
            columns=m.columns
        )
    else:
        # Backward-compatible handling if an older 8-column menus.csv is used.
        new = pd.DataFrame(
            [[
                rid,
                item_id,
                name,
                meal_type,
                category,
                serving_mass_g,
                emission_factor,
                quantity_unit
            ]],
            columns=m.columns
        )

    pd.concat([m, new], ignore_index=True).to_csv(MENUS, index=False)