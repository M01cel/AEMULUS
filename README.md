# AEMULUS 0.1 · Windows x64

Menedżer Android Virtual Device dla testów aplikacji na ekranach 1024 × 600 i 1280 × 720. Każda rozdzielczość ma osobny dysk Androida. Panel desktopowy steruje procesem emulatora. Obraz Androida, dotyk myszą i przeciąganie obsługuje osobne okno Android Emulator.

## Pobieranie aplikacji

[Pobierz instalator dla Windows x64](https://github.com/M01cel/AEMULUS/releases/latest). Instalator zawiera Python i Tcl/Tk. Po instalacji otwórz AEMULUS z menu Start. Android SDK i obraz systemu przygotuj według punktów 1, 3 i 4 poniżej. Punkty 2 i 5 dotyczą wersji źródłowej.

## Pierwsze uruchomienie

1. Przygotuj Windows 10/11 x64 na procesorze Intel z VT-x/EPT lub AMD z SVM. Sprawdź wirtualizację w Menedżerze zadań. Dla WHPX włącz „Platforma hiperwizora systemu Windows” w funkcjach Windows, jeśli jest potrzebna. Zmiana może wymagać administratora i restartu. Sam AEMULUS uruchamiaj jako zwykły użytkownik. Dla konfiguracji ze Studio i emulatorem planuj co najmniej 16 GB RAM i 16 GB wolnego miejsca. Nie określono pomiarowo minimum dla samego panelu.
2. Zainstaluj Python 3.12 x64 z python.org z Tcl/Tk oraz poleceniem py. Pakiet źródłowy korzysta wyłącznie z biblioteki standardowej. Wariant EXE budowany przez workflow zawiera interpreter.
3. W Android Studio otwórz SDK Manager. Zanotuj Android SDK Location. W SDK Tools zainstaluj Android SDK Command-line Tools (latest), Android Emulator oraz Android SDK Platform-Tools. Narzędzia wiersza poleceń wymagają Javy. Możesz użyć JBR dołączonego do Android Studio.
4. W PowerShell przygotuj obraz AOSP Android 14. Dostosuj ścieżki, jeśli instalacja jest niestandardowa. Przeczytaj warunki pakietów i zaakceptuj je samodzielnie w instalatorze.

~~~powershell
$Sdk = "$env:LOCALAPPDATA\Android\Sdk"
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
& "$Sdk\cmdline-tools\latest\bin\sdkmanager.bat" "--sdk_root=$Sdk" "system-images;android-34;default;x86_64"
& "$Sdk\emulator\emulator.exe" -accel-check
~~~

5. Rozpakuj cały ZIP. W tym samym PowerShell uruchom z katalogu projektu `.\AEMULUS.cmd`, aby przekazać JAVA_HOME do programu. Dwuklik działa po skonfigurowaniu Javy na stałe. W „Ustawienia” wskaż SDK, jeśli zainstalowano je w innej lokalizacji. Domyślny przydział to 2048 MiB i 2 vCPU. Nowe limity obowiązują od kolejnego startu.
6. Wybierz Car Head Unit 1024 × 600 i kliknij Start. Pierwszy start tworzy AVD oraz dysk danych. Po komunikacie „Android gotowy” odblokuj ekran Androida, jeżeli jest zablokowany.
7. „Instaluj APK” przyjmuje pojedynczy plik .apk. Jeśli pobierasz artefakt Actions, rozpakuj również jego ZIP. Wybierz pakiet dev.universalcarlauncher.app i „Uruchom aplikację”. Dla innej aplikacji wpisz jej identyfikator w edytowalnym polu pakietu.
8. W oknie emulatora przeciągaj myszą między ekranami. W panelu sprawdź Back, Home, zapis PNG i logcat działającego procesu. „Domyślny launcher” otwiera wybór aplikacji ekranu głównego w Androidzie. Wybierz H3LM i naciśnij Home. Powtórz instalację dla nowszego APK podpisanego tym samym kluczem. Różne podpisy powodują odmowę aktualizacji. Odinstalowanie usuwa dane aplikacji.
9. Wybierz Stop i sprawdź Status. Zamknięcie samego panelu pozwala ponownie podłączyć panel do uruchomionego AVD. Po błędzie rozruchu okno emulatora można zamknąć bezpośrednio. ADB jest współdzielonym narzędziem SDK i jego serwer może pozostać aktywny dla Android Studio.

## Diagnostyka i architektura

| Moduł | Odpowiedzialność |
|---|---|
| desktop.py | Tk/ttk, wybór profilu, ustawienia, kolejka wyników operacji w tle, ostatnio uruchamiane pakiety |
| devices.py | Model profilu i konfiguracja AVD, atomowy zapis ustawień użytkownika |
| engine.py | Uruchamianie narzędzi SDK, tworzenie AVD, wykrywanie sesji, oczekiwanie na gotowość Androida, zatrzymywanie |
| bridge.py | Rozwiązanie aktywności LAUNCHER lub HOME, walidacja pakietu i zrzut PNG |
| Diagnostyka w panelu | Wyniki poleceń, bieżąca pamięć gościa na żądanie, zapis logcat według PID aplikacji |

Dane, ustawienia i emulator.log znajdują się w %LOCALAPPDATA%\AEMULUS. Przy komunikacie o braku pliku sprawdź ścieżkę SDK i zakładkę SDK Tools. Przy błędzie Javy uruchom program z tym samym JAVA_HOME co sdkmanager. Gdy hypervisor jest niedostępny, sprawdź wynik -accel-check. Przy awarii aplikacji zapisz emulator.log. Eksport logcat z panelu wymaga działającego procesu. Po awarii procesu można odczytać pełny bufor przez adb -s NUMER logcat -d.

## Stan weryfikacji

Wykonano 6 testów jednostkowych na Linuxie i kompilację składni modułów. Testy sprawdzają powtarzalną konfigurację AVD, pomijanie USB i urządzeń offline, odmowę skierowania operacji do obcego profilu, wybór aktywności HOME, walidację pakietu i odrzucenie błędnej odpowiedzi przy zrzucie PNG. Odpowiedzi ADB w tych testach są zastąpione kontrolowanymi danymi.

Środowisko wykonawcze nie miało Windows, dostępu do /dev/kvm, emulatora, adb ani ekranu dla Tk. Rozruch Androida, wynikowa orientacja i rozmiar PNG, instalacja H3LM, gesty, wybór HOME, reinstalacja i zwolnienie pamięci po Stop wymagają próby na Windows. Workflow przygotowuje EXE dla Windows. Sam plik EXE i jego uruchomienie nie zostały tu zweryfikowane.

## Budowanie i plan następnej wersji

Na Windows uruchom poniższe polecenia z katalogu projektu. Gotowy folder dystrybucyjny to dist\AEMULUS. Przenoś go w całości.

~~~powershell
py -3 -m unittest -v
py -3 -m pip install pyinstaller==6.16.0
py -3 -m PyInstaller --clean --noconfirm --windowed --onedir --name AEMULUS desktop.py
~~~

1. Przeprowadzić scenariusz z punktów 5–9 na Windows 10 i 11. Zapisać wersje SDK, CPU, RAM, czas zimnego startu, rozmiar PNG, logcat oraz zachowanie H3LM po Home i aktualizacji. Sprawdzić też odłączony hypervisor, równoległe podłączenie telefonu i odmowę aktualizacji przy innym podpisie.
2. Dodać pomiar CPU i RAM procesu hosta, obsługę anulowania rozruchu i automatyczny stan wszystkich urządzeń.
3. Rozszerzyć model o profile telefonu, tabletu i własne API/DPI/orientację. Zweryfikować ABI bibliotek natywnych oraz funkcje zależne od Google Play Services dla oddzielnych obrazów.
4. Po testach przygotować podpisany instalator. CANBUS, OBD2, tuner i przyciski producenta wymagają odrębnych adapterów testowych. Obecny profil odtwarza ekran i wejście standardowego Androida.

## Źródła

- [Android Emulator i opcje startowe](https://developer.android.com/studio/run/emulator-commandline)
- [Akceleracja na Windows](https://developer.android.com/studio/run/emulator-acceleration)
- [Wymagania Android Studio i emulatora](https://developer.android.com/studio/install)
- [ADB](https://developer.android.com/tools/adb)
- [Warunki Android SDK](https://developer.android.com/studio/terms)
- [Analiza kandydatów](RESEARCH.md)
