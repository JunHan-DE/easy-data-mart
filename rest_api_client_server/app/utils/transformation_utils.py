from app.models import user_data
from app.database.schema.user_data import user_data


def create_mapping_instance(item: user_data) -> user_data:
    item_dict = add_postback_type(item)
    brandi_postback = user_data(
        advertising_id=item_dict['advertising_id'],
        idfa=item_dict['idfa'],
    )

    return brandi_postback


def add_postback_type(item: user_data) -> dict:
    item_dict = item.dict()
    if item.event_time:  # if postback is in app postback, event_time should be contained.
        item_dict.update({"is_in_app_postback": True, "is_install_postback": False})
    else:
        item_dict.update({"is_in_app_postback": False, "is_install_postback": True})

    return item_dict

