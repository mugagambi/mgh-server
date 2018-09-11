from decouple import config


def project_name(request):
    name = config('PROJECT_NAME')
    return {'PROJECT_NAME': name}
