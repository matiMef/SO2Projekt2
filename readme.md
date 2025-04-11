# Serwer Czatu

Ten projekt implementuje wielowątkowy serwer czatu oraz klienta w języku Python.

---

## 1. Wprowadzenie

Projekt składa się z dwóch głównych elementów:
- **Serwera:** Odpowiedzialnego za przyjmowanie połączeń od wielu klientów, rozsyłanie wiadomości, przechowywanie historii czatu oraz obsługę specjalnych poleceń.
- **Klienta:** Dostarcza prosty interfejs graficzny (GUI), dzięki któremu użytkownik może wysyłać i odbierać wiadomości.

---

## 2. Instrukcje Uruchomienia Projektu

### Wymagania wstępne
- **Python:** Upewnij się, że masz zainstalowaną odpowiednią wersję Pythona na swoim systemie.
- **Repozytorium:** Sklonuj repozytorium projektu na swój komputer.

### Budowanie projektu
1. Otwórz terminal i przejdź do katalogu projektu.
2. Uruchom polecenie:
   ```
   make
3. Uruchom serwer:
   ```
   ./Server
4. Uruchom klienta:
   ```
   ./Client
5. Ewentualna obsługa innych klientów - uruchomienie klienta na osobnym oknie terminalu

6. Czyszczenie:

   ```
   make clean
---
## 3. Opis Problemu cel projektu

- Stworzenie serwera czatu, który
obsługuje wielu klientów jednocześnie.

- Zapewnienie bezpiecznego dostępu do wspólnych zasobów (w środowisku wielowątkowym) dzięki użyciu blokad (mutex).

- Przechowywanie historii czatu.

- Dodatkowa obsługa specjalnych komend, które umożliwiają m.in. rozłączanie klientów oraz czyszczenie historii czatu.
---
## 4. Architektura Wielowątkowości
### Serwer


**Wątki obsługi klienta** - Każdy klient, który łączy się z serwerem, jest obsługiwany przez oddzielny wątek. Odpowiedzialne jest on za przyjmowanie wiadomości, komunikację z serwerem oraz obsługę rozłączenia klienta.

### Klient


**Wątek odbioru** - Ciągle nasłuchuje wiadomości z serwera i natychmiast aktualizuje GUI, aby użytkownik miał bieżący podgląd konwersacji. Odbiera dane i wyświetla je w konsoli.

---
## 5. Zarządzanie Współdzielonymi Zasobami i Synchronizacja

Aby zapewnić poprawne działanie w środowisku wielowątkowym, stosuje się mechanizmy synchronizacji:

**Współdzielone dane**:
   - *Lista clients*:
Przechowuje aktywne połączenia. Dostęp do niej jest zabezpieczony **blokadą (mutex)**, aby przy jednoczesnych operacjach (dodawanie/usuwanie klientów) nie dochodziło do błędów.

   - *Słownik names*:
Mapuje połączenia na nazwy użytkowników. Również zabezpieczony przez **blokadę**, aby zapewnić poprawną synchronizację przy modyfikacjach.

   - *Lista chat_history*:
Przechowuje historię wiadomości czatu. Dodawanie nowych wpisów oraz udostępnianie historii odbywa się z wykorzystaniem **blokady**, co zapobiega problemom przy jednoczesnym dostępie.

   - *Wyjście na Konsolę*:
**Lock** dla konsoli (cout_lock):
Używany do ochrony przed mieszaniem się komunikatów wypisywanych na konsolę przez różne wątki, co poprawia czytelność logów serwera.

   - *Rozsyłanie Wiadomości*:
Funkcja broadcast() wysyła wiadomości do wszystkich klientów. Aby uniknąć problemów wynikających z modyfikacji listy clients podczas iteracji, tworzona jest jej kopia przy użyciu **clients.copy()**. To rozwiązanie gwarantuje, że lista nie ulegnie zmianie w trakcie rozsyłania wiadomości.
---
## 6. Specjalne Komendy
W projekcie zaimplementowano kilka specjalnych komend:

- **!DISCONNECT**:
Pozwala klientowi na bezpieczne rozłączenie się z serwerem.

- **!CLS**:
Czyści historię czatu dla wszystkich użytkowników.
---
## 7. Podsumowanie
Projekt serwera czatu został zaprojektowany z myślą przede wszystkim o równoczesnej obsłudze wielu klientów oraz bezpiecznym dostępie do współdzielonych zasobów (dzięki mechanizmom synchronizacji).



