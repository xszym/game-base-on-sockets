# Tank game base on sockets

## Podstawowe założenia 
- [x] Jako program zaliczeniowy rozumiemy parę programów serwer i klient.
- [x] serwer ma możliwość obsługi wielu klientów jednocześnie.
- [x] W każdym z programów należy zaimplementować własny protokół
    - [ ] dokładnie określić typ i format dozwolonych wiadomośc
- [ ] Komendy protokołu wraz z ich parametrami, powinny być dokładnie zdefiniowanie i opisane pliku imitującym dokumentację techniczną
    - [ ] http://libgadu.net/protocol/#ch1.1
- [ ] Należy zadbać o prawidłową obsługę błędów każdej funkcji w programie
- [x] W projektach nie korzystamy z gotowych bibliotek.
- [ ] Brak któregokolwiek z plików w paczce oddanej jako program zaliczeniowy (w paczce powinien znaleźć się program klienta, program serwera, opis protokołu, opis uruchomienia programu) skutkuje brakiem zaliczenia.


### Uzyskanie większej liczby punktów niż 50 wymaga:
- [x] 1. zaimplementowania logiki, która wykorzystuje więcej niż 3 rodzaje przesyłanych wiadomości oraz  
- [ ] 2. wykorzystania co najmniej 1 mechanizmu z poniższych:
    ~~a. synchronizacja wątków,~~
    - [ ] b. obsługa większej liczby graczy niż dwóch jednocześnie,                                      
    ~~c. obsługa wielu procesów równolegle,~~

### Uzyskanie większej liczby punktów niż 65 wymaga:
- [ ] 1. spełnienia warunków z punktu powyższego oraz
- [ ] 2. wykorzystania co najmniej 2 z poniższych mechanizmów:
        ~~a. inna architektura niż klient-serwer, ~~
        ~~b. asynchroniczność (p2p),~~
    - [ ] c. serwer zdarzeniowy, 
    - [ ] d. połączenia szyfrowane.  


## Schemat programu
1. Przy pierwszym podłączeniu Klient i Serwer wymieniają się kluczami :) 
2. Klient może stworzyć lub dołączyć do pokój (2 przyciski)
Tworzenie: (1 napis i 1 przycisk)
- [x] Po kliknięciu stwórz pokój dostaje kod dołacznia do pokóju od serwara
- [ ] otrzymuje ile osób dołączyło 
- [ ] Ma przycisk START GAME
Dołączenie. (same napisy)
- [ ] dołącza do kanały 
- [ ] otrzymuje ile osób jest w pokóju
- [ ] ma napis czekanie na hosta


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
- [ ] Są roomy
- [ ] czekamy na osoby
- [ ] mogą być invide (np. po kodzie)
- [ ] wysyłanie i odbieranie na odzielnym wątku
- [ ] wymiana kluczy na początku (rejstracja)


## Setup
- ```pip install -r requirements.txt```


## Run
- ```python server.py```
- ```python client.py```


## Links 
https://gamedev.stackexchange.com/questions/20425/game-logic-on-the-server-good-or-bad


## Encrypt 
https://stackoverflow.com/questions/27287306/sending-encrypted-strings-using-socket-in-python

https://riptutorial.com/python/topic/8710/sockets-and-message-encryption-decryption-between-client-and-server

https://hub.packtpub.com/protect-tcp-tunnel-implementing-aes-encryption-with-python/

https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256


# TODO
- [x] Kolizja pomiędzy czołgami 
- [x] Kolizja z pociskiem
- [ ] Życie
- [ ] END GAME
- [ ] START_GAME od hosta
- [ ] Pokazywanie ilośći połączonych graczy
- [ ] SZYFORWANIE = Enkrypcja i dekrypcja 
- [ ] Nickname wysyłać od klienta i przypisać go do playera
- [ ] Odkomendować wiele roomów 
- [ ] Join do serwera po Kodzie
- [ ] Pokazywanie roomów 
- [ ] Serwer zdarzeniowy
- [ ] Testy i obsługa błędów


# Bugs
- [ ] Jak klient się rozłącza to nie usuwa go z listy połączonych graczy (quit do menu -> wysla do serwera ze wychodzi z gry, serwer usuwa gracza z listy)
- [ ] Możliwość sepownowania dwóch czołgów w tym samym miejscu (ekran podzielony na 4 czesci, w zaleznosci od nr gracza w innej czesci sie spawnuje) 


