import os
import sys
import django
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import base64
from io import BytesIO

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from recipe_scraper import scrape_menunedeli_recipe
from recipes.models import Recipe, Ingredient, Step

class Command(BaseCommand):
    help = 'Import recipes from menunedeli.ru URLs'

    def add_arguments(self, parser):
        parser.add_argument('--urls', nargs='+', help='URLs to import')
        parser.add_argument('--file', help='File containing URLs')

    def handle(self, *args, **options):
        # Set UTF-8 encoding for Windows console
        import sys
        if sys.platform == 'win32':
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        urls = [
            "https://menunedeli.ru/recipe/ovoshhi-v-duxovke-zapechennye-krupnymi-kuskami/",
            "https://menunedeli.ru/recipe/zharenaya-sparzha/",
            "https://menunedeli.ru/recipe/shpinatnye-bliny/",
            "https://menunedeli.ru/recipe/salat-so-shpinatom-pomidorami-i-ogurcami/",
            "https://menunedeli-ru.turbopages.org/turbo/menunedeli.ru/s/recipe/ovsyanye-vafli/",
            "https://menunedeli.ru/recipe/shokoladnye-pp-konfety-s-bananom/",
            "https://menunedeli.ru/recipe/venskie-vafli-iz-syra-i-yaic-na-zavtrak/",
            "https://menunedeli.ru/recipe/kukuruza-v-duxovke-v-folge-s-maslom/",
            "https://menunedeli.ru/recipe/zhyulen-v-bulochkax-goryachee-na-novogodnij-stol/",
            "https://menunedeli.ru/2013/11/recept-salata-iz-fasoli-s-orexami/",
            "https://menunedeli.ru/recipe/ovoshhnoe-ragu-s-fasolyu/",
            "https://menunedeli.ru/recipe/salat-s-vetchinoj-i-fasolyu/",
            "https://menunedeli.ru/recipe/postnyj-salat-s-fasolyu-konservirovannoj/",
            "https://menunedeli.ru/recipe/zharenaya-struchkovaya-fasol-s-yajcom/",
            "https://menunedeli.ru/recipe/pryanyj-sup-s-chechevicej-i-bolgarskim-percem/",
            "https://menunedeli.ru/recipe/salat-iz-svezhej-kapusty-i-morkovi/",
            "https://menunedeli.ru/recipe/kotlety-morkovnye-recept-klassicheskij/",
            "https://menunedeli.ru/recipe/morkovnoe-pechene-s-greckimi-orexami/",
            "https://menunedeli.ru/recipe/salat-s-kapustoj-morkovyu-i-ogurcom/",
            "https://menunedeli.ru/recipe/kabachki-s-kartoshkoj-i-kapustoj/",
            "https://menunedeli.ru/recipe/shhi-iz-svezhej-kapusty-s-kuricej/",
            "https://menunedeli.ru/recipe/kapusta-s-sosiskami-na-skovorode/",
            "https://menunedeli.ru/recipe/funchoza-s-kuricej-i-ovoshhami-s-soevym-sousom-na-skovorode/",
            "https://menunedeli.ru/recipe/kurinye-okorochka-v-duxovke/",
            "https://menunedeli.ru/recipe/kurinye-krylyshki-v-medovo-soevom-souse-v-duxovke/",
            "https://menunedeli.ru/recipe/pryanye-tefteli-iz-chechevicy-i-bulgura/",
            "https://menunedeli.ru/recipe/chechevica-na-garnir-recept-v-post/",
            "https://menunedeli.ru/recipe/salat-s-rukkoloj-i-kedrovymi-oreshkami/",
            "https://menunedeli.ru/recipe/gnyozda-iz-makaron-s-farshem-v-duxovke/",
            "https://menunedeli.ru/recipe/kartofelnye-gnezda-s-gribami/",
            "https://menunedeli.ru/recipe/kak-prigotovit-tofu-vkusno-i-bystro-v-domashnix-usloviyax/",
            "https://menunedeli.ru/recipe/postnyj-morkovnyj-pirog/",
            "https://menunedeli.ru/recipe/pirog-s-molodoj-belokochannoj-kapustoj-i-yajcami/",
            "https://menunedeli.ru/recipe/tefteli-s-grechkoj/",
            "https://menunedeli.ru/recipe/ovoshhnoe-ragu-s-kabachkami-i-kartoshkoj/",
            "https://menunedeli.ru/recipe/tushenyj-kartofel-s-chechevicej/",
            "https://menunedeli.ru/recipe/pasta-fettuchini-s-kuricej-i-gribami-v-slivochnom-souse/",
            "https://menunedeli.ru/recipe/zapekanka-iz-kabachkov-s-yajcami-v-duxovke/",
            "https://menunedeli.ru/recipe/zapekanka-s-tvorogom-v-duxovke-pyshnaya-s-yablokami/",
            "https://menunedeli.ru/recipe/kabachkovye-vafli/",
            "https://menunedeli.ru/recipe/tvorozhnye-vafli-v-vafelnice/",
            "https://menunedeli.ru/recipe/kurinaya-grudka-v-citrusovom-marinade/",
            "https://menunedeli.ru/recipe/kurica-s-ovoshhami-na-skovorode/",
            "https://menunedeli.ru/recipe/ragu-iz-baklazhanov/",
            "https://menunedeli.ru/recipe/tushenye-baklazhany-s-pomidorami-i-chesnokom/",
            "https://menunedeli.ru/recipe/ovoshhnaya-lazanya-s-kabachkami-i-baklazhanami/",
            "https://menunedeli.ru/recipe/kish-s-lukom-poreem-i-tuncom/",
            "https://menunedeli.ru/recipe/salat-s-kuricej-i-fasolyu/",
            "https://menunedeli.ru/recipe/kish-s-gribami-i-syrom/",
            "https://menunedeli.ru/recipe/kak-vkusno-prigotovit-cvetnuyu-kapustu/",
            "https://menunedeli.ru/recipe/svinina-v-duxovke-v-folge/",
            "https://menunedeli.ru/recipe/beze-recept-klassicheskij/",
            "https://menunedeli.ru/recipe/amerikanskij-tykvennyj-pirog/",
            "https://menunedeli.ru/recipe/tort-snikers/",
            "https://menunedeli.ru/recipe/kurica-teks-meks/",
            "https://menunedeli.ru/recipe/kurinye-nozhki-v-duxovke-s-risom/"
        ]

        if options['urls']:
            urls = options['urls']
        elif options['file']:
            with open(options['file'], 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]

        successful_imports = 0
        failed_imports = 0

        for url in urls:
            try:
                self.stdout.write(f"Importing from: {url}")
            except UnicodeEncodeError:
                self.stdout.write(f"Importing from URL...")
            
            # Check if recipe already exists
            if Recipe.objects.filter(source_url=url).exists():
                self.stdout.write(self.style.WARNING(f"Recipe already exists, skipping: {url}"))
                continue
            
            result = scrape_menunedeli_recipe(url)
            
            if result['success']:
                try:
                    # Create recipe
                    recipe = Recipe.objects.create(
                        title=result['title'],
                        source_url=url
                    )
                    
                    # Create ingredients
                    for ingredient_data in result['ingredients']:
                        Ingredient.objects.create(
                            recipe=recipe,
                            name=ingredient_data['name'],
                            quantity=ingredient_data['quantity'],
                            unit=ingredient_data['unit']
                        )
                    
                    # Create steps
                    for step_data in result['steps']:
                        step = Step.objects.create(
                            recipe=recipe,
                            order=step_data['order'],
                            description=step_data['description']
                        )
                        
                        # Handle photo if present
                        if 'photo_data' in step_data:
                            try:
                                image_data = base64.b64decode(step_data['photo_data'])
                                image_file = ContentFile(image_data, name=f'step_{step_data["order"]}_photo.jpg')
                                step.photo.save(f'step_{step_data["order"]}_photo.jpg', image_file, save=True)
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"Failed to save photo for step {step_data['order']}: {e}"))
                    
                    successful_imports += 1
                    try:
                        self.stdout.write(self.style.SUCCESS(f"Successfully imported: {result['title']}"))
                    except UnicodeEncodeError:
                        self.stdout.write(self.style.SUCCESS("Successfully imported recipe"))
                    
                except Exception as e:
                    failed_imports += 1
                    self.stdout.write(self.style.ERROR(f"Failed to save recipe: {e}"))
            else:
                failed_imports += 1
                self.stdout.write(self.style.ERROR(f"Failed to scrape: {result['error']}"))
        
        self.stdout.write(f"\nImport completed:")
        self.stdout.write(f"Successful: {successful_imports}")
        self.stdout.write(f"Failed: {failed_imports}")