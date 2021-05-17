# Tank game base on sockets

## Podstawowe założenia 
- [ ] Jako program zaliczeniowy rozumiemy parę programów serwer i klient.
- [ ] serwer ma możliwość obsługi wielu klientów jednocześnie.
- [ ] W każdym z programów należy zaimplementować własny protokół
    - [ ] dokładnie określić typ i format dozwolonych wiadomośc
- [ ] Komendy protokołu wraz z ich parametrami, powinny być dokładnie zdefiniowanie i opisane pliku imitującym dokumentację techniczną
    - [ ] http://libgadu.net/protocol/#ch1.1
- [ ] Należy zadbać o prawidłową obsługę błędów każdej funkcji w programie
- [ ] W projektach nie korzystamy z gotowych bibliotek.
- [ ] Brak któregokolwiek z plików w paczce oddanej jako program zaliczeniowy (w paczce powinien znaleźć się program klienta, program serwera, opis protokołu, opis uruchomienia programu) skutkuje brakiem zaliczenia.


### Uzyskanie większej liczby punktów niż 50 wymaga:
    - [ ] 1. zaimplementowania logiki, która wykorzystuje więcej niż 3 rodzaje przesyłanych wiadomości oraz  
  
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
- [ ] Po kliknięciu stwórz pokój dostaje kod dołacznia do pokóju od serwara
- [ ] otrzymuje ile osób dołączyło 
- [ ] Ma przycisk START GAME
Dołączenie. (same napisy)
- [ ] dołącza do kanały 
- [ ] otrzymuje ile osób jest w pokóju
- [ ] ma napis czekanie na hosta

## Komunikacja
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