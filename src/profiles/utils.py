import pycountry


def get_valid_regions(country_code: str) -> set[str]:
    return {
        subdivision.name
        for subdivision in pycountry.subdivisions
        if subdivision.country_code == country_code
    }


