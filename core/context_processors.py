from decouple import config


def project_name(request):
    app = config('APP_NAME')
    if app == 'demo':
        name = 'AgriSale'
    else:
        name = 'Meru Greens Horticulture Ltd'
    return {'PROJECT_NAME': name}
