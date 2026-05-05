# Projektanleitung

Diese Anleitung erklärt, welche Dokumente erstellt werden müssen,
was darin steht und in welcher Reihenfolge man vorgeht.
Als Beispiel dient das Projekt **HTLingo** (Vokabeltrainer).


## Überblick: Was muss abgeliefert werden

| # | Dokument | Wann | Zweck |
|---|----------|------|-------|
| 1 | **Projektauftrag** | Projektstart | Verbindliche Vereinbarung – formaler Projektstart |
| 2 | **Aufwandsschätzung** | Nach Projektauftrag | Wie lange dauert die Entwicklung? Wie viele Stunden werden benötigt? |
| 3 | **Pflichtenheft** | Nach Projektauftrag | Wie wird es technisch umgesetzt? |
| 4 | **Arbeitspakete** | Nach Pflichtenheft | Was genau wird gemacht, von wem und bis wann? |
| 5 | **Gantt-Diagramm** | Nach Arbeitspaketen | Arbeitspakete als Balken mit Terminen und Meilensteinen |
| 6 | **Testprotokoll** | Nach Entwicklung | Wurde alles getestet? |
| 7 | **README** | Abschluss | Wie startet man die App? |
| 8 | **Präsentation / Pitch** | Projektabschluss | Vorstellung beim Kunden |


## Schritt 0: Projektbegründung & Projektidee
- Brainstorming
- Mindmap
- Projektbegründung

## Schritt 1: Projektauftrag

Der Projektauftrag ist das verbindliche Dokument zwischen Auftraggeber und Projektteam.
Er legt Inhalt und Rahmenbedingungen des Projekts fest und markiert den formalen Projektbeginn.
Erst nach Unterzeichnung durch alle Beteiligten gilt das Projekt als offiziell gestartet.


| Abschnitt | Inhalt |
|-----------|--------|
| **Projektbezeichnung** | Kurzer, möglichst treffender Name des Projekts |
| **Projektauftraggeber** | Institution, Person oder Abteilung, die das Projekt in Auftrag gibt |
| **Projekthintergrund** | Sinn und Zweck – warum gibt es dieses Projekt? |
| **Projektendergebnis** | Was liegt am Ende vor? Welche messbaren Eigenschaften hat es? |
| **Projektziel(e)** | Haupt- und Teilziele; optional: Nicht-Projektziele (Abgrenzung) |
| **Projektbeschreibung** | Hauptaufgaben, Vorgehensweise, Methoden, erwartete Qualität |
| **Projektphasen / Meilensteine** | Tabelle: Phase – Ergebnis – Soll-Termin – Freigabe |
| **Projektstart / Projektende** | Offizielles Start- und Enddatum mit auslösendem Ereignis |
| **Projektressourcen** | Grobkalkulation: Personal, Infrastruktur, Material, Kosten |
| **Projektrisiken** | Bekannte Risiken und geplante Gegenmaßnahmen |
| **Projektorganisation** | Projektleitung, Teamrollen, Lenkungsausschuss |
| **Abschluss / Unterschriften** | Datum und Unterschriften aller Verantwortlichen |

### Beachte
- Keine Implementierungsdetails (JWT, REST, Docker) – das kommt ins Pflichtenheft
- Ziele müssen messbar formuliert sein ("läuft in unter 3 Sekunden", nicht "soll schnell sein")
- Ohne klare Abgrenzung (Nicht-Ziele) entsteht später Streit über den Projektumfang
- Erst beschreiben, dann coden – der Projektauftrag ist der formale Startschuss

## Schritt 2: Aufwandsschätzung

Die Aufwandsschätzung ermittelt vor der Entwicklung, wie lange das Projekt dauert und wie
viele Personenstunden benötigt werden. Sie bildet die Grundlage für den Zeitplan (Gantt).

Als Verfahren wird die **T-Shirt-Size-Methode** eingesetzt. Jede Anforderung bekommt
eine Größe statt einer exakten Stundenzahl. Einfach und gut geeignet für frühe Phasen.
Schätzt einen bekannten Aufwand und gebt dem eine Größe (z.B. M). Davon ausgehend
könnt ihr die anderen Aufwände schätzen. Größer (L), viel Größer (XL)

#### Größen und Stunden-Richtwerte

| Größe |  Bedeutung                                     |
|-------|------------------------------------------------|
| XS    | Triviale Aufgabe, kein nennenswertes Risiko   |
| S     | Überschaubar, bekannte Lösung                 |
| M     | Normaler Arbeitsaufwand, wenig Unbekanntes    |
| L     | Komplex, Unbekannt oder viel Abstimmung nötig |
| XL    | Sehr groß – sollte aufgeteilt werden          |

#### Vorgehen

1. Alle Anforderungen auflisten
2. Im Team jede Anforderung mit einer Größe versehen (Diskussion bei Abweichungen)
3. Stunden pro Größe aufaddieren Gesamtaufwand
4. Mit verfügbarer Kapazität vergleichen,  Scope anpassen falls nötig

#### Ergebnis der Schätzung (HTLingo)

| Anforderung | Größe | Aufwand (h) |
|-------------|-------|-------------|
| FA01 – Registrierung + Login | M | 8 |
| FA02 – Decks verwalten | S | 4 |
| FA03 – Karten verwalten | S | 4 |
| ...| 
| **Gesamt** | | **60 h** |

Verfügbare Kapazität: 80, scope passt.

### Beachte
- Größen im Team gemeinsam vergeben – Abweichungen zeigen Unklarheiten auf
- XL-Anforderungen immer aufteilen, bevor sie ins Gantt kommen
- Richtwerte (h pro Größe) einmalig zu Projektbeginn festlegen und nicht mehr ändern


## Schritt 3: Pflichtenheft

Das Pflichtenheft beantwortet die Frage: *Wie* werden die Anforderungen technisch umgesetzt.
Es ist die Antwort des Projektteams an den Auftraggeber.

### Besteht aus

|            | Inhalt | Beispiel |
|-------------------|--------|---------|
| Ausgangslage      | Ist-Zustand, Problemstellung, warum wird das Projekt gemacht | Schüler lernen mit Papier-Karteikarten, kein Fortschritt trackbar |
| Ist Zustand       | Bestehende Systeme/Prozesse und deren Schwächen | Anki zu komplex, Duolingo kostenpflichtig |
| Zielsetzung       | Soll-Zustand, Ziele, Nicht-Ziele (Abgrenzung) | Webanwendung mit Lern- und Abfragemodus |
| Anforderung       | Funktionale + nicht-funktionale Anforderungen mit Priorität | FA01–FA09, NF01–NF05 mit Beschreibung |
| Ui-Konzept        | Wireframes / Mockups der wichtigsten Seiten | Login, Deck-Übersicht, Lernmodus |
| Lieferobjekte     | Was wird geliefert, Abnahmekriterien je Lieferobjekt | Prototyp gilt als abgenommen wenn FA01–FA05 bestanden |


#### Technische Doku

|                   | Inhalt | Beispiel |
|-------------------|--------|---------|
| Architektur       | Systemarchitektur-Diagramm (Frontend / Backend / DB) | React Express PostgreSQL |
| Datenkatalog   | Tabellen, Spalten, Beziehungen | User, Deck, Card, Progress |
| ERD               | Entity Relationship Diagram | DBI Unterricht
| API-Dokumentation | Alle Endpunkte: Methode, Pfad, Request, Response, Auth | `POST /api/login`, `GET /api/decks` |
| Setup             | Wie kann das System gestartet/installiert werden | Es wird node und Docker benötigt |
| Testkonzept       | Testfälle für alle Muss-Anforderungen | TC01: Login mit korrekten Daten Redirect zur Übersicht |


### Gefahren bei fehlender oder mangelhafter technischer Dokumentation
- Pflichtenheft ohne API-Doku: man weiß selbst nicht was man baut, und die Schnittstelle ändert sich ständig
- Kein ERD: Datenbankstruktur wird beim Coden mehrfach umgebaut, kostet Zeit
- Testkonzept weglassen: keine Abnahme möglich
- Architekturdiagramm vergessen: das Team arbeitet aneinander vorbei


## Schritt 4: Arbeitspakete

Arbeitspakete zerlegen die Phasen aus dem Projektauftrag in konkrete, zuweisbare Aufgaben.
Jedes Paket hat einen Verantwortlichen, einen Zeitraum und ein klares Abnahmekriterium.
Sie sind die Grundlage für das Gantt-Diagramm.


### Beachte
- Jedes Arbeitspaket braucht genau eine verantwortliche Person – nicht „beide" für alles
- Abnahmekriterium muss prüfbar sein, kein vages „fertig"
- AP sind Milestones zugeordnet.

## Schritt 5: Zeitplanung (Gantt-Diagramm)

Wer macht was bis wann? Ein Gantt-Diagramm zeigt Aufgaben als Balken.

### Meilensteine

Meilensteine sind überprüfbare Zwischenergebnisse mit einem festen Termin – keine Tätigkeiten,
sondern abgeschlossene Zustände. Im Gantt werden sie als Raute eingetragen.

**Wann werden Meilensteine festgelegt?**
- **Grob:** bereits im Projektauftrag (eine Zeile pro Phase mit Soll-Termin und Freigabe)
- **Detailliert:** hier im Gantt mit konkreter Kalenderwoche

**Beispiel HTLingo:**

| Meilenstein | Ergebnis | KW    |
|-------------|----------|-------|
| M1          | Pflichtenheft vom Betreuer freigegeben | KW 15 |
| M2          | Entwicklungsumgebung läuft (PoC erfolgreich) | KW 16 |
| M3          | Backend vollständig, alle API-Endpunkte testbar | KW 17 |
| M4          | Alle Muss-Anforderungen im Frontend implementiert | KW 20 |
| M5          | Alle Muss-Anforderungen im Frontend implementiert | KW 20 |
| M6          | Testprotokoll vollständig ausgefüllt | KW 23 |
| M7          | Abschlusspräsentation gehalten, Projekt abgenommen | KW 24 |

### Tipps
- Parallel-Arbeit einplanen: in einem 2er-Team kann Frontend und Backend gleichzeitig laufen
- Puffer für Testing und Bugfixing einplanen – das dauert immer länger
- Nicht Pflichtenheft schreiben als Meilenstein – sondern Pflichtenheft freigegeben


## Schritt 6: Entwicklung (Code)

Erst wenn Projektauftrag, Pflichtenheft und Zeitplan stehen, fängt das Coden an.
Wer vorher einfach drauflos programmiert, baut meistens das Falsche oder muss alles nochmal umbauen.

**Reihenfolge empfohlen:**
1. Datenbank aufsetzen
2. Backend
3. Frontend
4. Features von innen nach außen: erst API, dann UI dazu 


## Schritt 7: Testen

Jeder fertige Endpunkt, jedes Feature im Frontend wird **sofort** getestet.

Das **Testprotokoll** ist kein optionales Extra – ohne es kann es bei der Abnahme nicht bewiesen werden,
dass die App funktioniert.

- Jeden Testfall aus dem Testkonzept durchführen
- Testfortschrittsberichte
- Ergebnis (bestanden / fehlgeschlagen) und Datum eintragen
- Fehlgeschlagene Tests: entweder beheben oder als bekannte Einschränkung dokumentieren
- Fehler mit einer geeigneten Fehlermeldung erstellen (Siehe Folien!)


## Schritt 8: README & Abschlussdokumentation

Das README erklärt jemandem, der den Code noch nie gesehen hat, wie er die App starten kann.
Mit einem Test auf einem fremden Rechner kann geprüft werden ob es vollständig ist.

Checkliste Abschluss:
- [ ] Alle Pflichtenheft-Kapitel vollständig?
- [ ] ERD vorhanden?
- [ ] API dokumentiert?
- [ ] Testprotokoll ausgefüllt?
- [ ] README getestet?


## Schritt 9: Präsentation / Kunden-Pitch

10-15 Minuten. Struktur:
1. Problem (warum gibt es das Projekt?)
2. Lösung (was wurde gebaut?)
3. Live-Demo der Kernfunktionen
4. Was würde man mit mehr Zeit noch bauen?
5. Lessons Learned

Die Demo muss live funktionieren. Vorher einen Probelauf machen, es muss auch live geändert werden können.
