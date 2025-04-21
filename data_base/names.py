from names_dataset import NameDataset

def get_names(n: int, country: str) -> list[str]:
    nd = NameDataset()
    country = country
    result = nd.get_top_names(n=n, gender='Male', country_alpha2=country)
    names = result[country]['M']
    return names