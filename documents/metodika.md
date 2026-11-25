# Skaičiavimo metodika

Naudojamas vartotojo pasirinktas užduoties pristatymo metodas: atskaitos reikšmių diapazonas padalijamas į devynis **vienodo pločio intervalus**. Tai nėra šalių padalijimas į devynias vienodo dydžio reitingo grupes.

## Formulė

Kiekvieno kriterijaus intervalų plotis `h = (max − min) / 9`. Kai didesnė reikšmė laikoma palankesne pasirinkto kriterijaus prasme, normalizuota reikšmė yra `z = (x − min) / (max − min)`. Kai mažesnė reikšmė palankesnė, `z = (max − x) / (max − min)`.

Balas yra `min(9, max(1, ceil(9 × z)))`. Taip vidinė riba patenka į žemesnį intervalą, o pats minimumas ir maksimumas patenka į 1 arba 9 balą, priklausomai nuo krypties. Pavyzdžiui, kai min=10, max=100 ir didesnė reikšmė palankesnė, 10 bei 20 duoda 1, 20,01 duoda 2, o 100 duoda 9. Skaičiuojama iš išsaugoto skaitinio tikslumo; dokumento lentelėse reikšmės apvalinamos tik rodymui.

Abiem nagrinėjamoms teritorijoms konkretaus kriterijaus ribos vienodos. Nė vienas balas nėra ranka priskirtas pagal norimą rezultatą. Skaičiavimus galima atkurti `python scripts/score.py`.

## Etalonai

- WDI: to paties rodiklio ir metų šalys bei teritorijos su duomenimis, be regioninių agregatų; pridėta Taivano nacionalinė reikšmė. Nacionalinių apklausų ir modeliuotų įverčių palyginimai orientaciniai.
- PWT 11.0: atskiros ekonomikos su tikrais to metų duomenimis. PGP darbo našumo ir vartojimo rodikliams taikomas paties šaltinio `i_outlier=Regular` filtras. Darbo pajamų dalis nėra PGP kainų perskaičiavimas, todėl tam kriterijui šis kainų išskirčių filtras netaikomas.
- Švietimas: nurodytų lyginamųjų lentelių bendrų metų imtys. Atmestos kitų metų ar nesuderinamos aprėpties eilutės. EDU03 Kinijos reikšmė pridėta iš tų pačių metų nacionalinio šaltinio; mokytojų apskaitos skirtumai išlieka.
- Energija ir CO2: to metų OWID serijos įrašai su trijų raidžių ISO kodais ir faktinėmis reikšmėmis; regioniniai agregatai atmesti. Imtyse yra ir priklausomų teritorijų.
- H5, H6 ir ENV6: devynios Rytų ir Pietryčių Azijos ekonomikos — Taivanas, Kinija, Japonija, Pietų Korėja, Singapūras, Tailandas, Vietnamas, Malaizija ir Mianmaras. Tai tikslinė mokomoji palyginimo imtis, ne reprezentatyvus viso regiono ar pasaulio reitingas.

`data/indicators.json` saugomi visi panaudoti imčių nariai, šaltinių URL, metai, ribos ir formulės. Mažoms IHME imtims nurodytos viešai diagramose rodomos suapvalintos faktinės reikšmės; pilnas riboto platinimo pirminis duomenų rinkinys neperpublikuotas.

## Visos ribos ir rezultatai

Rodyklė aukštyn reiškia, kad didesnė reikšmė gauna didesnį balą; rodyklė žemyn reiškia apverstą skalę. Lentelės ribos suapvalintos rodymui. Skaičiavimas naudoja visą JSON tikslumą.

| Kodas | Kriterijus | Kryptis | Metai | Imties n | Min. | Maks. | Taivano balas | Kinijos balas |
|---|---|:---:|---|---:|---:|---:|---:|---:|
| ECO01 | BVP vienam gyventojui | ↑ | 2024 | 201 | 216,23 | 288 001,57 | 2 | 1 |
| ECO02 | Darbo našumas: realusis BVP vienam dirbančiajam | ↑ | 2023 | 177 | 2 277,23 | 262 154,52 | 5 | 2 |
| ECO03 | Nedarbo lygis | ↓ | 2024 | 183 | 0,13 | 34,64 | 9 | 8 |
| ECO04 | Moterų dalyvavimas darbo rinkoje nuo 15 metų | ↑ | 2024 | 183 | 4,71 | 82,92 | 6 | 7 |
| ECO05 | Darbo pajamų dalis BVP | ↑ | 2023 | 140 | 8,44 | 75,06 | 8 | 7 |
| ECO06 | Užimtųjų dalis tarp 15 metų ir vyresnių gyventojų | ↑ | 2024 | 183 | 21,27 | 87,11 | 5 | 6 |
| ECO07 | Realusis namų ūkių ir valdžios vartojimas vienam gyventojui | ↑ | 2023 | 181 | 883,81 | 59 842,03 | 7 | 2 |
| EDU01 | Aukštojo mokslo bendrasis įtraukties rodiklis (GER) | ↑ | 2022 | 27 | 64,6 | 116,2 | 5 | 2 |
| EDU02 | Vidutinė mokymosi trukmė tarp 25 metų ir vyresnių | ↑ | 2022 | 24 | 6,6 | 14,3 | 8 | 2 |
| EDU03 | Pradinio ugdymo mokiniai vienam mokytojui | ↓ | 2021 | 15 | 11 | 19,2 | 8 | 4 |
| EDU04 | Tyrėjai (viso etato ekvivalentais) | ↑ | 2021 | 11 | 3,2 | 17,3 | 8 | 1 |
| EDU05 | MTEP išlaidos | ↑ | 2021 | 27 | 1,1 | 5,6 | 6 | 3 |
| EDU06 | Fiksuoto plačiajuosčio ryšio prenumeratos | ↑ | 2024 | 152 | 0 | 55,68 | 5 | 8 |
| EDU07 | SCIE mokslinės publikacijos | ↑ | 2022 | 30 | 87,48 | 4 549,8 | 3 | 1 |
| H1 | Tikėtina gyvenimo trukmė gimus | ↑ | 2023 | 218 | 54,46 | 86,37 | 8 | 7 |
| H2 | Kūdikių mirtingumas | ↓ | 2023 | 197 | 1,3 | 71,9 | 9 | 9 |
| H3 | Vaikų iki penkerių metų mirtingumas | ↓ | 2023 | 197 | 1,3 | 116,8 | 9 | 9 |
| H4 | Naujagimių mirtingumas | ↓ | 2023 | 197 | 0,6 | 39,5 | 9 | 9 |
| H5 | Mirtingumas nuo širdies ir kraujagyslių ligų | ↓ | 2023 | 9 | 73,7 | 472,3 | 9 | 6 |
| H6 | Mirtingumas nuo vėžio | ↓ | 2023 | 9 | 83,2 | 142,7 | 1 | 5 |
| H7 | Ligoninių lovos | ↑ | 2023 | 74 | 0,35 | 9,77 | 6 | 6 |
| ENV1 | Teritorinės CO₂ emisijos vienam gyventojui | ↓ | 2023 | 218 | 0,04 | 32,84 | 6 | 7 |
| ENV2 | Vartojimu pagrįstos CO₂ emisijos vienam gyventojui | ↓ | 2023 | 120 | 0,15 | 31,48 | 6 | 7 |
| ENV3 | Atsinaujinančių išteklių dalis elektros gamyboje | ↑ | 2023 | 210 | 0 | 100 | 1 | 3 |
| ENV4 | Anglies dalis elektros gamyboje | ↓ | 2023 | 207 | 0 | 98,76 | 6 | 4 |
| ENV5 | Elektros gamybos gyvavimo ciklo emisijų intensyvumas | ↓ | 2023 | 210 | 0 | 1 306,14 | 5 | 5 |
| ENV6 | Mirtingumas, priskiriamas oro taršai | ↓ | 2023 | 9 | 17,1 | 286,5 | 9 | 7 |
| ENV7 | Pirminės energijos intensyvumas | ↓ | 2022 | 165 | 0,24 | 4,84 | 8 | 7 |

## Kaip interpretuoti profilį

1. Balas nusako vietą **intervale pasirinktoje imtyje**, o ne absoliučią socialinę ar ekologinę normą. Didelių etalono išskirčių paveikti intervalai gali daug ekonomikų sutelkti į tą patį balą.
2. Atskirų kriterijų etalonai ir metai skiriasi. Negalima iš ratų ploto apskaičiuoti vienos „darnesnės šalies“ ar oficialaus DVT reitingo. H6 Taivano 1 balas reiškia didžiausią vėžio mirtingumo reikšmę tik pasirinktoje devynių ekonomikų imtyje.
3. Darbo našumas, BVP ir vartojimas susiję. Vaikų mirtingumo rodikliai persidengia. Energetikos ir emisijų rodikliai bei oro taršos ir ligų naštos rodikliai taip pat susiję. Dėl to bendras arba sričių balų vidurkis neskaičiuojamas.
4. Darbo pajamų dalis BVP matuoja darbo ir kapitalo pajamų santykį. Tai nėra Gini indeksas, atlyginimų mediana ar nelygybė tarp namų ūkių. Vartojimo kriterijus apima namų ūkius ir valdžią.
5. Mirtingumo nuo vėžio, širdies ir kraujagyslių ligų bei oro taršai priskiriami rodikliai standartizuoti pagal amžių ir modeliuoti. Nenaudojama taisyklė, kad vyresnė gyventojų struktūra savaime blogesnė. Modelių neapibrėžtumo intervalai šioje paprastoje skalėje nepavaizduoti.
6. Paveikslėliai yra pasirinktos metodikos mokomasis rezultatas, o ne oficialus valdžios, UNDP ar kitų duomenų teikėjų įvertinimas. Politikos efektyvumo priežastiniam vertinimui reikėtų papildomų tyrimų.
