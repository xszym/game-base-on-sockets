# Tank game base on sockets
2D tank game where you can:
- Play with your friends
- Host own game
- Join to others servers
- Become CHAMPION of this game


## Podstawowe założenia 
- [x] Jako program zaliczeniowy rozumiemy parę programów serwer i klient.
- [x] serwer ma możliwość obsługi wielu klientów jednocześnie.
- [x] W każdym z programów należy zaimplementować własny protokół
    - [ ] dokładnie określić typ i format dozwolonych wiadomośc
- [x] Komendy protokołu wraz z ich parametrami, powinny być dokładnie zdefiniowanie i opisane pliku imitującym dokumentację techniczną
    - [ ] http://libgadu.net/protocol/#ch1.1
- [ ] Należy zadbać o prawidłową obsługę błędów każdej funkcji w programie
- [x] W projektach nie korzystamy z gotowych bibliotek.
- [ ] Brak któregokolwiek z plików w paczce oddanej jako program zaliczeniowy (w paczce powinien znaleźć się program klienta, program serwera, opis protokołu, opis uruchomienia programu) skutkuje brakiem zaliczenia.


### Uzyskanie większej liczby punktów niż 50 wymaga:
- [x] 1. zaimplementowania logiki, która wykorzystuje więcej niż 3 rodzaje przesyłanych wiadomości oraz  
- [x] 2. wykorzystania co najmniej 1 mechanizmu z poniższych:
    ~~a. synchronizacja wątków,~~
    - [x] b. obsługa większej liczby graczy niż dwóch jednocześnie,                                      
    ~~c. obsługa wielu procesów równolegle,~~

### Uzyskanie większej liczby punktów niż 65 wymaga:
- [x] 1. spełnienia warunków z punktu powyższego oraz
- [ ] 2. wykorzystania co najmniej 2 z poniższych mechanizmów:
        ~~a. inna architektura niż klient-serwer, ~~
        ~~b. asynchroniczność (p2p),~~
    - [x] c. serwer zdarzeniowy, 
    - [ ] d. połączenia szyfrowane.  


## Schemat programu
1. Przy pierwszym podłączeniu Klient i Serwer wymieniają się kluczami :) 
2. Klient może stworzyć lub dołączyć do pokój (2 przyciski)
Tworzenie: (1 napis i 1 przycisk)
- [x] Po kliknięciu stwórz pokój dostaje kod dołacznia do pokóju od serwara
Dołączenie. (same napisy)
- [x] Dołączanie do kanału


## Komunikacja
### Example
Auth:None\n\r
Command:Register\n\r
Status:SUCC\n\r
Lenght:123\n\r\n\r
<len o długości 123>\n\r\n\r

Rodzaje wiadmości:
 - [ ] REGISTER, (login)
     - SUCC, key
     - ERR, msg
 - [ ] START_CHANNEL
     - SUCC, join_key
     - ERR, msg
 - [ ] JOIN_CHANNEL
     - SUCC, 
     - ERR, msg
 - [ ] UPDATE_CHANNEL
 - [ ] START_GAME
 - [ ] UPDATE_GAME


## Można
- [x] Są roomy
- [x] mogą być invide (np. po kodzie)
- [x] wysyłanie i odbieranie na odzielnym wątku
- [ ] wymiana kluczy na początku (rejstracja)


## Setup
- ```pip install -r requirements.txt```


## Run
- ```python server.py```
- ```python client.py``` for public server
- ```python client.py -L``` for own local server


## SLL 
https://docs.python.org/3/library/ssl.html

# TODO
- [ ] SZYFORWANIE = Enkrypcja i dekrypcja 
- [ ] Testy i obsługa błędów


# Bugs
- [ ] NIe obsłgujemy błędów gdy serwer jest całgowicie wyłączony
