from ruamel.yaml import YAML
from collections import namedtuple

doc = """
Валовый внутренний продукт (ВВП):
   comment:
       Comment text
       on 2 lines
   charts:
       - title: ВВП, темп прироста за 12 мес.
         names: GDP_yoy
       - title: Инвестиции, темп прироста за 12 мес.
         names: INVESTMENT_yoy

Выпуск:
   comment:
       Comment text
       on 2 lines
   charts:
       - title: Промышленное производство, темп прироста за 12 мес.
         names: INDPRO_yoy
       - title: Сельское хозяйство, темп прироста за 12 мес.
         names: AGROPROD_yoy

Цены:
   charts:
       - names: CPI_rog
         title: Индекс потребительских цен (ИПЦ), в % пред.периоду
       - names: CPI_FOOD_rog, CPI_NONFOOD_rog, CPI_SERVICES_rog
         title: ИПЦ по компонентам, в % пред.периоду


Дефицит(-)/профицит бюджета:
   charts:
       - names: GOV_SURPLUS_FEDERAL_bln_rub
         title: Федеральный бюджет, млрд.руб.
       - names: GOV_SURPLUS_SUBFEDERAL_bln_rub
         title: Региональные бюджеты, млрд.руб.

Внешняя торговля:
   charts:
       - names: EXPORT_GOODS_bln_usd, IMPORT_GOODS_bln_usd
         title: Экспорт и импорт товаров, млрд.долл.
       - names: TRADE_SURPLUS_bln_usd
         title: Сальдо торгового баланса, млрд.долл.


"""

Chart = namedtuple('Chart', 'names title filename')


def as_chart(d):
    title = d['title']
    names = [s.strip() for s in d['names'].split(',')]
    filename = f"{'_'.join(names)}.png"
    return Chart(names, title, filename)


yaml = YAML()
z = yaml.load(doc)
CHARTS_DICT = {k: list(map(as_chart, v['charts']))
               for k, v in z.items()}
print(CHARTS_DICT)
