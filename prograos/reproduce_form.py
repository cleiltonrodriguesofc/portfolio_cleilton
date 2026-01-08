from prograos.forms import CalculadoraFreteForm
import django
import os
import sys
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_cleilton.settings')
django.setup()


def run_simulation():
    print("--- Checking Form Validity ---")
    data = {
        'custo_grao_por_saco': '60,00',
        'preco_base_venda_por_saco': '62,00',
        'frete_por_tonelada': '1.400,00',
        'quantidade': '1.000,000',
        'unidade_quantidade': 'sacos'
    }

    form = CalculadoraFreteForm(data=data)

    if form.is_valid():
        print("Form IS VALID")
        print(f"Cleaned Data: {form.cleaned_data}")
    else:
        print("Form IS INVALID")
        print(f"Errors: {form.errors}")


if __name__ == '__main__':
    run_simulation()
