# Interaktyvūs Darnūs ratai

Tai mokomoji „Circles of Sustainability“ **Profile Circles** adaptacija Taivano ir žemyninės Kinijos užduočiai. Naudojami tie patys 28 patikrinti kriterijai ir 56 balai kaip pagrindiniame darbe. Kiekviena sritis turi septynis kriterijus, o kiekvienas kriterijus vertinamas devynių balų skale.

**[Atverti interaktyvius ratus](https://PovilasJan.github.io/taiwan-china-storymaps/)**

## Ryšys su originaliu metodu

Originalus modelis apima ekologiją, ekonomiką, politiką ir kultūrą. Užduoties aprašymo 3 puslapyje nurodyta šabloną pritaikyti šioms sritims: ekonomikai, švietimui ir technologijoms, sveikatai ir demografijai, ekologijai. Todėl šiame papildyme naudojami užduoties kriterijai.

Perimta apskritimo sandara ir spalvų principas: žemesni balai raudoni, vidurinis geltonas, aukštesni žali. Sektoriaus užpildymo ilgis ir spalva rodo jo balą. Nepaspalvinti išoriniai langeliai padeda matyti likusią devynių žingsnių skalę. Šaltinis: [Circles of Sustainability — Profile Circles](https://www.circlesofsustainability.com/circles-overview/profile-circles/).

**Spalvos čia reiškia santykinį intervalą pasirinktoje imtyje.** Jos nesuteikia oficialaus „kritinio“, „bazinio“ ar „gyvybingo“ darnumo statuso. Balas 5 nėra pasaulio vidurkis ar mediana. Balas 9 nereiškia, kad DVT pasiektas. Taikoma anksčiau pasirinkta [vienodo pločio intervalų metodika](metodika.md); originalaus modelio kokybinės etiketės nepriskiriamos statistiniams balams.

## Naudojimas

Pasirinkite kriterijų sąraše arba ant rato. Pamatysite abiejų teritorijų faktines reikšmes, metus, vienetus, balus, palankią kryptį, atskaitos imties ribas ir šaltinių nuorodas. Spalvą papildo skaitiniai balai, todėl rezultatą galima perskaityti nepasikliaujant vien spalva.

Įjungę **Scenarijų**, galite pakeisti pasirinkto kriterijaus balą slankikliu arba paspausdami rato žiedą. Tai demonstracinis bandymas: pirminės reikšmės ir duomenimis apskaičiuoti balai lieka matomi atskirai ir nekeičiami. Pakeitimai laikomi tik atvertame puslapyje. Išjungus režimą grįžtama prie faktinio profilio; mygtukas „Atkurti visus pradinius balus“ panaikina demonstracinius pakeitimus. Scenarijaus eksportas pažymimas „SCENARIJUS – ne faktinis vertinimas“.

Paveikslėliams naudokite prie kiekvieno rato esančius PNG arba SVG eksporto mygtukus. Paruošti didelės raiškos PNG taip pat yra saugykloje:

- [Taivano Profile Circle](../assets/taivano-profile-circle.png)
- [Kinijos Profile Circle](../assets/kinijos-profile-circle.png)

Failai `docs/index.html`, `docs/app.js`, `docs/style.css` ir `docs/indicators.js` veikia kartu. Atsisiuntus visą saugyklą, `docs/index.html` galima atverti naršyklėje ir be serverio ar interneto; interneto reikia tik išorinėms šaltinių nuorodoms.

## Įdėjimas į StoryMaps

Paprasčiausias būdas — įkelti du naujus PNG į `Swipe` bloką vietoje ankstesnių ratų. Abu variantai naudoja identiškus balus; naujojo spalva žymi balą, ankstesnio — sritį.

Interaktyvumui pridėkite `Embed` bloką ir įrašykite viešą puslapio adresą `https://PovilasJan.github.io/taiwan-china-storymaps/`. Jei StoryMaps arba organizacijos nustatymai nerodo įterpto puslapio, naudokite nuorodos kortelę ir palikite PNG palyginimą. DOCX importas šio interaktyvaus bloko nesukuria.

Tai atitinka [oficialią Esri įterpimo instrukciją](https://doc.esri.com/en/arcgis-storymaps/latest/author-and-share/add-embeds.html): viešą puslapį galima pateikti kaip interaktyvų turinį arba kortelę, priklausomai nuo įterpimo galimybių.

Po ratu palikite trumpą paaiškinimą: „Mokomoji Circles of Sustainability adaptacija pagal 28 užduoties kriterijus. Spalvos rodo santykinį balą pasirinktoje imtyje, o ne oficialų darnumo statusą. Duomenys 2021–2024 m.“

## Atkūrimas ir kilmė

```bash
python scripts/build_interactive_data.py
python scripts/build_profile_circles.py
```

Skaičiavimų šaltinis yra `data/indicators.json`; naršyklės rinkinyje nekartojami visi etalonų nariai, tačiau visas jų sąrašas išlieka pagrindiniame JSON. HTML, SVG braižymas ir PNG generatorius sukurti šiam projektui. Originalios svetainės programinis kodas ar iliustracijos nekopijuoti. Modelio autorystė priskiriama „Circles of Sustainability“; jo svetainėje pateiktos naudojimo sąlygos taikomos originaliai medžiagai.
