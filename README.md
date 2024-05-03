# Symulacja_cyfrowa
Projekt Symulacja Cyfrowa
# 1. Treść Zadania
Rozważmy system radiokomunikacyjny składający się z N stacji bazowych posiadających R blo-
ków zasobów (ang. Resource Blocks). W losowych odstępach czasu 𝜏 (wynikającej z intensywno-
ści zgłoszeń λ) w każdej stacji bazowej pojawiają się użytkownicy. Każdy użytkownik zajmuje je-
den bloków na losowy czas μ. Jeśli stacja bazowa nie ma wystarczającej liczby bloków zasobów by
obsłużyć użytkownika jego zgłoszenie może być przekierowane do sąsiedniej stacji. Jeśli żadna ze
stacji bazowych nie może obsłużyć zgłoszenia jest ono tracone. Intensywność zgłoszeń w systemie
zmienia się cyklicznie: przez pierwsze 8 godziny intensywność zgłoszeń wynosi λ/2 przez kolejne
6 godzin - 3λ/4, następnie przez 4 godziny wynosi λ, po czym spada do wartości 3λ/4 na 6 godzin i
cykl się powtarza. Dla stacji bazowych można ustalić próg przejścia w stan uśpienia L (wyrażony
w % zajętych bloków zasobów). Stacja bazowa w stanie uśpienia pobiera moc równą 1 W, a pod-
czas gdy jest aktywna 200 W. Zgłoszenia z uśpionej stacji są przejmowane równomiernie przez są-
siednie stacje. Podobnie jeśli w jednej z sąsiednich komórkach przekroczony zostanie próg H (wy-
rażony w % zajętych bloków zasobów), uśpiona komórka jest aktywowana. Proces uśpienia i ak-
tywacji komórki trwa 50 ms i zużywa jednorazowo 1000 W.
Opracuj symulator sieci bezprzewodowej zgodnie z przypisaną metodą M (Tabela 1) oraz parame-
trami podanymi w Tabeli 3.\
● Za pomocą symulacji ustal maksymalną intensywność zgłoszeń λ, która zapewni, że żadne
zgłoszenia nie są tracone przez cały okres eksperymentu (z pominięciem fazy początkowej i
przy założeniu, że stacje bazowe nie będą usypiane).\
● Za pomocą symulacji, wyznacz wartość progu przejścia w stan uśpienia L, który zapewni, że
średnia dobowa liczba traconych zgłoszeń nie przekroczy 5%. Następnie wyznacz:\
o średnie dobowe zużycie energii w całym systemie\
o średnią dobową zajętość bloków zasobów w całym systemie\
o średnią dobową liczbę traconych zgłoszeń\
o średni dobowy czas uśpienia dla każdej stacji bazowej\
● Sporządź wykres średniego dobowego zużycia energii w całym systemie w funkcji progu
uśpienia L.\
● Sporządź wykres średniej dobowej liczby traconych zgłoszeń w całym systemie w funkcji
progu uśpienia L.\
# 2. Parametry
μ – zmienna losowa o rozkładzie równomiernym z zakresu <1:30> sekund\
τ - zmienna losowa o rozkładzie wykładniczym o intensywności λ\
H - 80%\