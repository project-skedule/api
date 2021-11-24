from distutils import text_file

from requests import get, post, put
from stringcolor import cs

API_HOST = "localhost"
API_PORT = "8009"
API_PREFIX = "/api"
API_URL = "http://" + API_HOST + ":" + API_PORT + API_PREFIX
SCHOOL = "/school"
CORPUS = "/corpus"
CABINET = "/cabinet"
SUBCLASS = "/subclass"
TEACHER = "/teacher"
STUDENT = "/student"
PARENT = "/parent"
LESSON = "/lesson"
LESSON_NUMBER = "/lessontimetable"
INFO = "/info"
REGISTRATION = "/registration"
ROLE_MANAGEMENT = "/rolemanagement"
ID_GETTER = "/idgetter"
LESSON_GETTER = "/lesson/get"

passed = 0
max_tests = 841

response = get("http://" + API_HOST + ":" + API_PORT)
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET index", "green"))

response = post(API_URL + SCHOOL + "/new", json={"name": "Бауманский лицей 1580"})
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully POST new school", "green"))
school_id = response.json()["id"]


response = get(API_URL + ID_GETTER + SCHOOL + f"/{school_id}")
assert response.status_code == 200, cs(response.text, "red")
passed += 1
assert response.json()["name"] == "Бауманский лицей 1580"
passed += 1
print(cs("Successfully GET school", "green"))

response = put(
    API_URL + SCHOOL + "/update",
    json={
        "school_id": school_id,
        "name": 'Государственное бюджетное общеобразовательное учреждение города Москвы "Бауманская инженерная школа № 1580"',
    },
)
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully UPDATE school", "green"))
school_id = response.json()["id"]


response = get(API_URL + ID_GETTER + SCHOOL + f"/{school_id}")
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET school", "green"))
assert (
    response.json()["name"]
    == 'Государственное бюджетное общеобразовательное учреждение города Москвы "Бауманская инженерная школа № 1580"'
)
passed += 1


response = post(
    API_URL + CORPUS + "/new",
    json={
        "address": "Балаклавский проспект, ~6А~",
        "name": "1ый корпус",
        "canteen_text": "Столовка не работает никогда, еда ужасная и страшная",
        "school_id": school_id,
    },
)
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully POST new corpus", "green"))
corpus1_id = response.json()["id"]

response = get(API_URL + ID_GETTER + CORPUS + f"/{corpus1_id}")
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["name"] == "1ый корпус"
passed += 1
assert rj["address"] == "Балаклавский проспект, ~6А~"
passed += 1

response = get(API_URL + INFO + CORPUS + "/canteen", json={"corpus_id": corpus1_id})
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["data"] == "Столовка не работает никогда, еда ужасная и страшная"
passed += 1

response = put(
    API_URL + CORPUS + "/update",
    json={
        "name": "1 корпус",
        "corpus_id": corpus1_id,
    },
)
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully UPDATE corpus", "green"))
corpus1_id = response.json()["id"]

response = get(API_URL + ID_GETTER + CORPUS + f"/{corpus1_id}")
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["name"] == "1 корпус"
passed += 1
assert rj["address"] == "Балаклавский проспект, ~6А~"
passed += 1


response = put(
    API_URL + CORPUS + "/update",
    json={
        "address": "Балаклавский проспект, 6А",
        "corpus_id": corpus1_id,
    },
)
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully UPDATE corpus", "green"))
corpus1_id = response.json()["id"]

response = get(API_URL + ID_GETTER + CORPUS + f"/{corpus1_id}")
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["name"] == "1 корпус"
passed += 1
assert rj["address"] == "Балаклавский проспект, 6А"
passed += 1


canteen_text = """БУФЕТ:
Понедельник-пятница - 9:00 - 15:00
Суббота - 10:00 - 14:00
СТОЛОВАЯ:
РАСПИСАНИЕ ЗАВТРАКОВ:
10ые классы - 9:40 - 9:50
11ые классы - 10:30 - 10:45
РАСПИСАНИЕ ОБЕДОВ:
10ые классы - 12:20 - 12:40
11ые классы - 13:20 - 13:40"""

response = put(
    API_URL + CORPUS + "/update",
    json={
        "canteen_text": canteen_text,
        "corpus_id": corpus1_id,
    },
)
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully UPDATE corpus", "green"))
corpus1_id = response.json()["id"]

response = get(API_URL + INFO + CORPUS + "/canteen", json={"corpus_id": corpus1_id})
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["data"] == canteen_text, cs(rj["data"], "red")
passed += 1


response = post(
    API_URL + CORPUS + "/new",
    json={
        "address": "Балаклавский проспект, ~6~",
        "name": "2ой корпус",
        "canteen_text": "Столовка не работает никогда, еда ужасная и страшная",
        "school_id": school_id,
    },
)
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully POST new corpus", "green"))
corpus2_id = response.json()["id"]

response = get(API_URL + ID_GETTER + CORPUS + f"/{corpus2_id}")
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["name"] == "2ой корпус"
passed += 1
assert rj["address"] == "Балаклавский проспект, ~6~"
passed += 1

response = put(
    API_URL + CORPUS + "/update",
    json={
        "name": "2 корпус",
        "corpus_id": corpus2_id,
    },
)
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully UPDATE corpus", "green"))
corpus2_id = response.json()["id"]

response = get(API_URL + ID_GETTER + CORPUS + f"/{corpus2_id}")
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["name"] == "2 корпус"
passed += 1
assert rj["address"] == "Балаклавский проспект, ~6~"
passed += 1


response = put(
    API_URL + CORPUS + "/update",
    json={
        "address": "Балаклавский проспект, 6",
        "corpus_id": corpus2_id,
    },
)
corpus2_id = response.json()["id"]
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully UPDATE corpus", "green"))

response = get(API_URL + ID_GETTER + CORPUS + f"/{corpus2_id}")
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["name"] == "2 корпус"
passed += 1
assert rj["address"] == "Балаклавский проспект, 6"
passed += 1

response = get(API_URL + INFO + CORPUS + "/canteen", json={"corpus_id": corpus2_id})
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["data"] == "Столовка не работает никогда, еда ужасная и страшная"
passed += 1
text = """СТОЛОВАЯ:

РАСПИСАНИЕ ЗАВТРАКОВ:
8ые классы - 9:40 - 9:50
9ые классы - 10:30 - 10:45
10-11ые классы - 11:25 - 11:40

РАСПИСАНИЕ ОБЕДОВ:
8ые классы - 12:20 - 12:40
9ые классы - 13:20 - 13:40
10-11ые классы - 14:20 - 14:40"""
response = put(
    API_URL + CORPUS + "/update",
    json={
        "canteen_text": text,
        "corpus_id": corpus2_id,
    },
)
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully UPDATE corpus", "green"))
corpus2_id = response.json()["id"]

response = get(API_URL + INFO + CORPUS + "/canteen", json={"corpus_id": corpus2_id})
assert response.status_code == 200, cs(response.text, "red")
passed += 1
print(cs("Successfully GET corpus", "green"))
rj = response.json()
assert rj["data"] == text
passed += 1

cabinets = """1 корпус, 317
1 корпус, 106
1 корпус, 306
1 корпус, акт.зал
1 корпус, 303
1 корпус, 120
1 корпус, 206
1 корпус, 316
1 корпус, 311
1 корпус, библ.
1 корпус, 105
1 корпус, 113
1 корпус, 209
1 корпус, 304
1 корпус, 305
1 корпус, 210
1 корпус, 309
1 корпус, 213
1 корпус, 301
1 корпус, 211
1 корпус, 208
1 корпус, 314
1 корпус, 312
1 корпус, 201
1 корпус, 302
1 корпус, 107
1 корпус, 205
1 корпус, 215а
1 корпус, 112
1 корпус, 215
1 корпус, 308
1 корпус, 207
1 корпус, 313
1 корпус, 124
1 корпус, 315
1 корпус, 212
1 корпус, 310
1 корпус, сп.зал/ трен.зал
1 корпус, сп.зал/трен.зал
1 корпус, 205 (2к)
1 корпус, 112/107
1 корпус, 112/библ
1 корпус, 107/библ
1 корпус, 107/стол
1 корпус, 107/106
1 корпус, 112/317
1 корпус, ?
1 корпус, 107/215а
2 корпус, 210
1 корпус, 317/112
2 корпус, ИТ-полигон
1 корпус, 107/311
1 корпус, 107/211
1 корпус, 112/117
1 корпус, 107/112
1 корпус, 2087
2 корпус, 317
2 корпус, 205
2 корпус, 310
2 корпус, 528
2 корпус, 425
2 корпус, 202
2 корпус, 529
2 корпус, 319
2 корпус, 315
2 корпус, сп.зал
2 корпус, 206
2 корпус, 532
2 корпус, 527
2 корпус, 311
2 корпус, 422
2 корпус, 313
2 корпус, 424
2 корпус, трен.зал
2 корпус, 207
2 корпус, 423
2 корпус, 314
2 корпус, 208
2 корпус, 201
2 корпус, 427
2 корпус, 531
2 корпус, 419
2 корпус, 316
2 корпус, 426
2 корпус, 428
2 корпус, ИТ-полигон лаб
2 корпус, 418
2 корпус, 318
2 корпус, 104
2 корпус, ?
2 корпус, 209
2 корпус, ИТ-полигон лаб3
2 корпус, ИТ-полигон лаб1
2 корпус, ИТ-полигон лаб2
2 корпус, ИТ-полигон лаб.
2 корпус, ИТ-полигон лаб.3
2 корпус, ИТ-полигон лаб.2
2 корпус, ИТ-полигон лаб.1
1 корпус, сп.зал""".split(
    "\n"
)
cabinet_ids = []
for cabinet in cabinets:
    corpus, name = cabinet.split(", ")
    corpus = corpus1_id if corpus == "1 корпус" else corpus2_id

    floor = int(name[0]) if name[0].isdigit() else 5 if name[0] == "И" else 1

    response = post(
        API_URL + CABINET + "/new",
        json={"corpus_id": corpus, "name": name + "Test", "floor": floor + 1},
    )
    assert response.status_code == 200, cs(response.text, "red")
    passed += 1
    print(cs("Successfully POST new cabinet", "green"))
    cab_id = response.json()["id"]

    response = get(API_URL + ID_GETTER + CABINET + f"/{cab_id}")
    assert response.status_code == 200, cs(response.text, "red")
    passed += 1
    print(cs("Successfully GET cabinet", "green"))
    rj = response.json()
    assert rj["floor"] == floor + 1
    passed += 1
    assert rj["name"] == name + "Test"
    passed += 1

    response = put(
        API_URL + CABINET + "/update",
        json={"cabinet_id": cab_id, "name": name, "floor": floor},
    )
    assert response.status_code == 200, cs(response.text, "red")
    passed += 1
    print(cs("Successfully UPDATE cabinet", "green"))
    cab_id = response.json()["id"]

    response = get(API_URL + ID_GETTER + CABINET + f"/{cab_id}")
    assert response.status_code == 200, cs(response.text, "red")
    passed += 1
    print(cs("Successfully POST cabinet", "green"))
    rj = response.json()
    assert rj["floor"] == floor
    passed += 1
    assert rj["name"] == name
    passed += 1
print()
print("=" * 50)
print(cs(f"Passed {passed}/{max_tests}", "white").bold())
