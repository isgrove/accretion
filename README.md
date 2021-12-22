# Accretion
Portfolio analytics for the intelligent investor

## Contributing

1. Create a pip environment and install the required packages using `pipenv install -r requirements.txt`

2. Install the node modules for the theme by navigating to `accretion/theme/static_src` and thenrun the command `npm install`

3. Now create a `secrets.py` file in the `accretion/accretion` directory and create the following variables
    * DJANGO_KEY
    * IEX_KEY
    * SENDGRID_API_KEY
4. All ready to go. Just you just need to run the Django server using `python3 manage.py runserver` and run the Tailwind server using `python3 manage.py tailwind start`