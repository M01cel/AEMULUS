# Wybór fundamentu · 21 listopada 2026

Wszystkie pięć podanych adresów było dostępnych. Informacje o funkcjach pochodzą ze źródeł projektów. Nie przeprowadzono niezależnych testów ich binariów. Liczby gwiazdek i forków to stan widoczny w odczycie GitHub i tylko pośredni wskaźnik zainteresowania.

| Projekt | Windows, Android i APK | Architektura i stan | Licencje i wniosek |
|---|---|---|---|
| [AndroidBox](https://github.com/Wolklaw/AndroidBox) | Windows 10/11, rzeczywisty Android Emulator, instalacja aplikacji | Python, PySide6, gRPC, SDL, wiele instancji, instalator i aktualizator. 117 commitów, 35 gwiazdek i 2 forki | Kod produktu MIT, osobne warunki zależności, obrazów i SDK. Najlepszy kandydat na fork. Aktualizacje w tle i funkcje gamingowe zwiększają zakres utrzymania. |
| [AndroidMulti](https://github.com/bionicdonkey/AndroidMulti) | Instrukcja Windows, Linux i macOS. System uruchamia emulator SDK. APK można instalować przez jego ADB. Instalatora APK w samym GUI nie potwierdzono. | Menedżer Python, klonowanie szablonów AVD i synchronizacja wejścia ADB. Wymaga istniejącego szablonu. Widoczne 0 gwiazdek i 0 forków. | Opis „as-is” nie wskazuje jednoznacznego zezwolenia na redystrybucję. Nie użyto kodu. |
| [AndroLink](https://github.com/FullDiveRS/AndroLink) | Windows, APK i prawdziwy Android przez backend Emulator lub QEMU. AdbBackend łączy z istniejącym Androidem. SimulatedBackend służy do innych zadań. | C#, Win32, Core, wymienne backendy i współdzielenie plików. 8 commitów, 0 gwiazdek i forków. Dojrzałość wymaga testu. | MIT dla projektu, dodatkowe informacje w LICENSE.md. Ciekawy punkt odniesienia dla rozbudowy, więcej backendów do objęcia testami. |
| [qemu-android](https://github.com/mirror/qemu-android) | Kod silnika Android Emulator z obsługą Windows. Potrzebny zgodny kernel i obraz. APK instaluje pakiet manager Androida przez ADB. | C/C++, CMake, Ninja, integracja urządzeń wirtualnych. Mirror kieruje wkład do upstream/Gerrit. Nie zweryfikowano aktualności domyślnej gałęzi względem dystrybucji SDK. | QEMU GPLv2, części mają własne warunki. Dystrybucja binariów wymaga analizy odpowiednich źródeł, licencji i notices. Koszt własnych kompilacji i utrzymania jest nieuzasadniony dla MVP. |
| [BlissOS](https://github.com/BlissOS) | Organizacja i system Android dla PC x86. Na hoście Windows wymaga maszyny wirtualnej lub osobnego rozruchu. Pakiety instaluje gość Android. | Wiele repozytoriów AOSP, kernel i komponenty PC. Widoczne gałęzie Android 13–15, aktualizacje w 2026, kanały Matrix, Telegram i Discord. | Manifest Apache-2.0, warunki zależą od komponentu, m.in. kernela. Zachowanie wymaganych notices, licencji i obowiązków źródłowych wymaga audytu konkretnego obrazu. Opcja późniejszego backendu. |

MIT przy przejęciu istotnej części kodu wymaga zachowania informacji copyright i treści zezwolenia. Licencja nakładki nie obejmuje automatycznie pozostałych komponentów. W AEMULUS napisano własny kod panelu. Archiwum źródłowe nie zawiera SDK, obrazu Androida, H3LM ani kodu tych pięciu projektów. SDK i obraz instaluje właściciel stanowiska z oficjalnego źródła na warunkach danego pakietu. Przed dystrybucją zamrożonego EXE trzeba dołączyć informacje licencyjne dla dołączonego Pythona i Tcl/Tk.

| Strategia | Korzyść | Koszt i decyzja |
|---|---|---|
| A. Fork AndroidBox | Najkrótsza droga do rozbudowanego GUI i integracji wejścia | Przejęcie zależności, modelu aktualizacji i rozwiązań gamingowych. |
| B. Własny panel i oficjalny emulator | Aktualizacje hypervisora, grafiki i ADB po stronie SDK. Niewielki panel i profile dopasowane do radia. | Własny cykl życia AVD i diagnostyka wymagają testów. Wybrano do implementacji. |
| C. Rozbudowa AndroidMulti | Klonowanie AVD i zarządzanie wieloma sesjami | Niejasne pozwolenie na redystrybucję i zależność od szablonów; synchronizacja wielu instancji ma niski priorytet. |

[QEMU Windows](https://www.qemu.org/download/) · [Licencja QEMU](https://www.qemu.org/docs/master/about/license.html) · [Licencja AndroLink](https://github.com/FullDiveRS/AndroLink/blob/main/LICENSE.md) · [Warunki SDK](https://developer.android.com/studio/terms)
