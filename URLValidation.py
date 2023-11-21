import validators
from validators import ValidationError

# Define public variables
aa_vars_list = []


class Validation:
    def valid_url(url):
        # Check if the parent URL has a scheme, if not, add "http://" prefix
        # if not url.startswith(("http://", "https://")):
        #     url = "http://" + url
        try:
            req = validators.url(url)
            while req != True:
                return Validation.valid_url(input('Please enter a valid url:'))
        except ValidationError as ex:
            print(f'Something went wrong: {ex}')
            print('Try again!')
            return Validation.valid_url(input('Please enter a valid url:'))

        return url


class DefineVariables:
    def analyticsVars():
        for i in range(75):
            prop = "c" + str(i)
            aa_vars_list.append(prop)

        for i in range(250):
            eVar = "v" + str(i)
            aa_vars_list.append(eVar)
        aa_vars_list.append("events")

        return aa_vars_list
