# Tank2D - Programowanie Aplikacji Sieciowych 2021
Kozacka gra w którą może grać, każdy, z każdym na całym świecie! ZOSTAŃ MISTRZEM CZOŁGÓW 2D!


## Features
- [x] Tworzenie pokojów (na nowym porcie)
- [x] Invide po kodzie
- [x] Wysyłanie i odbieranie na odzielnym wątku
- [x] Możliwość zmiany nicku w (nawet trakcie gry)
- [x] Rejstracja przy pierwszym podłączeniu
- [x] Przeglądanie dostępnych gier listowanych po nicku graczy
- [x] Szyfrowanie z użyciem ssl
- [x] Powolne tracenie życia po rozłączeniu się, do momentu ponownego podłączenia lub ŚMIECI
- [x] Zajęte miejsce po końcu gry
- [x] SUPER muzyka w tle, której nie da się wyłączyć!
- [x] Skonfigurowane CD (continuous deployment)
- [x] Limit możliwych gier w zależności od udostępnionych portów


# Setup
- ```pip3 install -r requirements.txt```


## Run Client for public server
- ```python3 client.py``` for public server or ```python client.py```


## Run own server

### Using Docker-compose (recommended)
```docker-compose up --build``` 

### or Python (NOT recommended)
```python3 server.py``` or ```python client.py```

### Client for local server
```python3 client.py -L``` or ```python3 client.py --local```
or 
```python client.py -L``` or ```python client.py --local```


# Dokumentacja i instrukcja
Pełna dokumentacja i rozszerzona instrukcja znajduje się w folderze `docs`.


# Podstawowe założenia 
- [x] Jako program zaliczeniowy rozumiemy parę programów serwer i klient.
- [x] serwer ma możliwość obsługi wielu klientów jednocześnie.
- [x] W każdym z programów należy zaimplementować własny protokół
    - [x] dokładnie określić typ i format dozwolonych wiadomośc
- [x] Komendy protokołu wraz z ich parametrami, powinny być dokładnie zdefiniowanie i opisane pliku imitującym dokumentację techniczną
- [x] Należy zadbać o prawidłową obsługę błędów każdej funkcji w programie
- [x] W projektach nie korzystamy z gotowych bibliotek.
- [x] Brak któregokolwiek z plików w paczce oddanej jako program zaliczeniowy (w paczce powinien znaleźć się program klienta, program serwera, opis protokołu, opis uruchomienia programu) skutkuje brakiem zaliczenia.


## Uzyskanie większej liczby punktów niż 50 wymaga:
- [x] 1. zaimplementowania logiki, która wykorzystuje więcej niż 3 rodzaje przesyłanych wiadomości oraz  
- [x] 2. wykorzystania co najmniej 1 mechanizmu z poniższych:
    ~~a. synchronizacja wątków,~~
    - [x] b. obsługa większej liczby graczy niż dwóch jednocześnie,                                      
    ~~c. obsługa wielu procesów równolegle,~~


## Uzyskanie większej liczby punktów niż 65 wymaga:
- [x] 1. spełnienia warunków z punktu powyższego oraz
- [x] 2. wykorzystania co najmniej 2 z poniższych mechanizmów:
        ~~a. inna architektura niż klient-serwer, ~~
        ~~b. asynchroniczność (p2p),~~
    - [x] c. serwer zdarzeniowy, 
    - [x] d. połączenia szyfrowane.  
