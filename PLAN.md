# NJE GAMF Kar - Szakdolgozat/Diplomamunka bejelentő 2025/2026-os tanév tavaszi félév

Metadata
> email: andras.balog@protonmail.com    
> Neptun kód: T4PIJ6           
> Szak: Programozó informatikus

## Szakdolgozat címe
- **HU**: IoT telemetria optimalizálás: bináris szerializáció és middleware alapú szenzor adat validálás
- **EN**: IoT telemetry optimization: binary serialization and middleware-based sensor data validation

## Téma rövid leírása (max. 5-10 mondat)
A szakdolgozatom az Internet of Things (IoT) telemetria optimalizálását vizsgálja erőforrás-korlátozott környezetekben. Ehhez az elterjedt JSON alapú adatstruktúra helyett bináris szerializálást (Protocol Buffers) és a sztenderd HTTP protokol helyett MQTT protokolt használok. 

Az architektúra poliglot megközelítésű, Python-t használva a szenzor-szimulációhoz, Go-t pedig a párhuzamos adatbeviteli motorhoz, amely képes a nagy mennyiségű egyidejű adatfolyamok kezelésére. A rendszer middleware-alapú feldolgozási lánc segítségével képes automatizált validációval biztosítani az adatok integritását, mielőtt azok az InfluxDB-be perzisztálásra kerülnének.

A teljes stack Podman segítségével konténerizálva van, ami biztonságos, rootless és reprodukálható telepítési környezetet biztosít. Végül a valós idejű vizualizáció Grafana segítségével valósul meg. A tanulmány hipotézise, hogy a bináris protokollok és a moduláris adatbeviteli logika kombinációja jelentősen javítja az IoT-infrastruktúra skálázhatóságát és megbízhatóságát.

## Fejezetek
1. **Bevezetés**                
Az IoT térnyerése, a korlátozott hálózatokban jelentkező adatforgalom kihívásai és az adatintegritás kritikus fontossága az adatbeviteli rétegben.
2. **IoT technológiák napjainkban és elméleti hátterük**          
Az MQTT mint átviteli protokoll feltárása, a szerializálási formátumok (JSON vs. Protobuf) összehasonlítása és az idősoros adatbázisok (TSDB) alapelveinek vizsgálata.
3. **Rendszerarchitektúra és implementációs terv**       
TBD
4. **Az IoT szenzor adat szimulációs réteg**      
Python-alapú mock szolgáltatás fejlesztése `paho-mqtt` használatával, szenzor viselkedések (hőmérséklet, páratartalom, gáz, ajtó) szimulálása és bináris szerializálási logika implemetálása.
5. **Nagy teljesítményű adatfeldolgozó motor**     
Go service implementációja, párhuzamos MQTT subscriber és a dekódoláshoz és feldolgozáshoz szükséges Middleware Pipeline kialakítása.
6. **Adatellenőrzési és integritási mechanizmusok**    
A validációs middleware kifejtése – tartományellenőrzések végrehajtása és hibás telemetria kezelése.
7. **Adat perzisztálás és vizualizáció**         
Protobuf és InfluxDB sémák összehangolása, Grafana irányítópult konfigurálása és a rendszer teljesítményének elemzése (késleltetés, átviteli sebesség és hibajelzés).
8. **Összefoglalás**           
Következtetések a bináris szerializáció előnyeiről, a Go/Python poliglot megközelítésből levont tanulságok és az edge-computing kiterjesztések lehetőségei.

## A szakdolgozat 1 oldalas idegen nyelvű összefoglalása

**IoT telemetry optimization: binary serialization and middleware-based sensor data validation**

My thesis examines the optimization of Internet of Things (IoT) telemetry in resource-constrained environments. To this end, I use binary serialization (Protocol Buffers) instead of the widely used JSON-based data structure, and the MQTT protocol instead of the standard HTTP protocol. 

The architecture is polyglot, using Python for sensor simulation and Go for the parallel data ingestion engine, which is capable of handling large amounts of concurrent data streams. The system uses a middleware-based processing chain to ensure data integrity through automated validation before data is persisted to InfluxDB.

Given the following thesis structure and page length where most of the theoretical part will be discussed in chapter 2., give me a detailed structure with relevant questions or topics to discuss in each chapter: 

**Chapters** - overall 28-35 pages
1. **Introduction** - 3 page
The rise of IoT, the challenges of data traffic in limited networks, and the critical importance of data integrity in the data entry layer.
2. **IoT technologies today and their theoretical background** - 8 pages          
Exploring MQTT as a transport protocol, comparing serialization formats (JSON vs. Protobuf), and examining the principles of time series databases (TSDB).
3. **System architecture and implementation plan** - 3 pages      
4. **The IoT sensor data simulation layer** - 3 pages
Development of a Python-based mock service using `paho-mqtt`, simulation of sensor behaviors (temperature, humidity, gas, door), and implementation of binary serialization logic. How different this simulated data from real life sensor data.
5. **High-performance data processing engine** - 3 pages     
Implementation of Go service, parallel MQTT subscriber, and development of Middleware Pipeline for decoding and processing.
6. **Data verification and integrity mechanisms** - 3 pages    
Development of validation middleware – execution of range checks and handling of faulty telemetry.
7. **Data persistence and visualization** - 3 pages         
Aligning Protobuf and InfluxDB schemas, configuring the Grafana dashboard, and analyzing system performance (latency, throughput, and error reporting).
8. **Summary** - 3 pages           
Conclusions on the advantages of binary serialization, lessons learned from the Go/Python polyglot approach, and possibilities for edge computing extensions.

Using the following sources:
### I. Core IoT & Communication Protocols
- [x] Banks, A., & Gupta, R. (2014). MQTT Version 3.1.1. OASIS Standard. (The official specification for your transport layer).
- [x] Hanes, D., et al. (2017). IoT Fundamentals: Networking Technologies, Protocols, and Use Cases for the Internet of Things. Cisco Press. (Great for comparing HTTP vs. MQTT).
- [x] Al-Fuqaha, A., et al. (2015). "Internet of Things: A Survey on Enabling Technologies, Protocols, and Applications." IEEE Communications Surveys & Tutorials. (A foundational paper for any IoT thesis).

### II. Data Serialization & Performance (Protobuf vs. JSON)
- [x] Google Developers (2023). Protocol Buffers Documentation. (The primary source for your binary serialization theory).
- [x] Sumaray, A., & Makki, S. K. (2012). "A Comparison of Data Serialization Formats for Optimal Efficiency on a Mobile Platform." ACM. (Empirical evidence for Protobuf efficiency).
- [x] Vinoski, S. (2006). "Advanced Message Queuing Protocol." IEEE Internet Computing. (Theoretical background on message-oriented middleware).

### IV. Databases & Visualization (InfluxDB & Grafana)
- [x] Naqvi, S. N. R., et al. (2017). "Time Series Databases and InfluxDB." International Journal of Computer Science and Information Security. (Theoretical justification for TSDB over Relational DBs).
- [x] Challis, K. (2022). Hands-On Dashboard Development with Grafana. Packt Publishing. (Documentation for your visualization layer).

### V. Containerization & Security (Podman)
- [x] Walsh, D. (2019). Podman in Action. Manning Publications. (The definitive source for explaining "rootless" and "daemonless" containerization).
- [x] Pahl, C., & Lee, B. (2015). "Containers and Clusters for Edge Computing." IEEE International Conference on Cloud Computing. (Connects Podman/Docker specifically to the IoT Edge).

### VI. Data Integrity & Validation
- [x] Fowler, M. (2002). Patterns of Enterprise Application Architecture. Addison-Wesley. (The theoretical origin of the "Pipeline" and "Middleware" patterns you are using).

# Szakdoga követelmények

## Formai követelmények
10.2. A dolgozat formai szerkezete   
1. Belső címoldal – Szakdolgozat c. sablon tartalmazza.   
2. A szakdolgozati/diplomamunka feladatlap egységvezető által jegyzett és OI által hitelesített példánya: letölthető a NEPTUN rendszerből.   
3. Nyilatkozat a saját munka készítéséről: Ezt a hallgatónak ki kell pipálnia (nem kell belerakni a dolgozatba) a NEPTUN rendszerben. E nélkül nem tudja a munkát beadni.  
4. A Szakdolgozati/Diplomamunka adatlap c. nyomtatvány, nem része a dolgozat dokumentációjának, csak a NEPTUN rendszerben van jegyezve, amelyet a tanszékek és konzulensek adminisztrálnak.   
5. Tartalomjegyzék   
6. Bevezetés (sorszám nélkül)   
7. A dolgozat érdemi része a Szakdolgozati sablon.doc sablonnak megfelelő formátumban  
8. Összefoglaló (sorszám nélkül)   
9. Ábrajegyzék (sorszám nélkül)   
10. Irodalomjegyzék pontos forrásmegjelöléssel (ld. 3.4. fejezet)    
11. Mellékletek jegyzéke és mellékletek   

## Terjedelem
- **28-35 oldal** mellékletek nélkül

## Szakirodalom és forrás
- Elméleti háttér 1/3-át kell hogy kitegye a szakdolgozatnak, **15-20 forrás**   

Az irodalomjegyzéket a szerzők nevei szerinti ABC sorrendben kell elkészíteni. A forrásként felhasznált műveket az alábbi bibliográfiai adatokkal kell szerepeltetni.     
Szakkönyvek esetén:     
    - a szerző(k) neve, a mű címe,    
    - szerkesztett kötetnél a szerkesztő(k) neve után a (szerk.) megjelöléssel   
    - a háromnál több szerzővel rendelkező műveknél a szerzők felsorolása helyett az első szerző nevét követően az és mtsai megjelölés alkalmazandó,   
    - a kiadó, a kiadás helye, éve.   
Folyóiratból vett cikkeknél:   
    - a szerző(k) neve a könyveknél leírt módon, a cikk címe,   
    - a folyóirat címe, kötetszáma, évszáma, a cikk helye (oldalszám mettől meddig).  
Internetes hivatkozásnál:   
    - a szerző(k) neve a könyveknél leírt módon, a cikk címe,   
    - webes cím (URL); a megtekintés dátuma.   
    
## Technológiai dokumentációk
??
Függetlenül attól, hogy a műveletterv vonatkozó rovatának kitöltése szükséges, a technológiai adatok pontos és részletes számítását csak a fontosabb műveleteknél célszerű bemutatni.

## Szoftvertermékek
A tervezés, fejlesztés és tesztelés során használt eljárások illetve a fejlesztői dokumentáció kivitelezése a szaktantárgyak feldolgozása során tanult szempontok, elvek szerint történik. A felhasználói dokumentációt a dolgozat mellékletében ill. webalkalmazás esetén a honlap megfelelő részeibe integrálva kell elhelyezni.

## A dolgozat és a további állományok felöltése
A szakdolgozat/diplomamunka és az azzal közös dokumentumban szerkesztett mellékleteket szöveges PDF-formátumban kell feltölteni az NEPTUN rendszerbe. A PDF-állománynak tartalmaznia kell a NEPTUN-ból letöltött oldalakat, és nem haladhatja meg a megengedett tárhelyméretet. A további dokumentumokat (technológiai dokumentáció, tervrajzok, nem beköthető mellékletek, szoftverfejlesztés esetén a magyarázatokkal ellátott forráskódok) egy ZIP-fájlban összecsomagolva kell feltölteni.

## Idegen nyelvű összefoglalás 
BSC SZAKOKON
–	szakdolgozatban **minimum 5 db idegen nyelvű forrás** használata
–	a szakdolgozat 1 oldalas angol vagy német nyelvű összefoglalót tartalmaz

Értékelés
–	szakdolgozat értékelése a szakirodalmi feldolgozásnál az idegen nyelvű szakirodalomra és az összefoglalásra is kiterjed

## Ábrajegyzék
Egy sima tartalomjegyzék dedikáltan az ábráknak

## Irodalomjegyzék

### I. Core IoT & Communication Protocols
- [x] Banks, A., & Gupta, R. (2014). MQTT Version 3.1.1. OASIS Standard. (The official specification for your transport layer).
- [x] Hanes, D., et al. (2017). IoT Fundamentals: Networking Technologies, Protocols, and Use Cases for the Internet of Things. Cisco Press. (Great for comparing HTTP vs. MQTT).
- [ ] Shelby, Z., & Bormann, C. (2009). 6LoWPAN: The Wireless Embedded Internet. Wiley. (Background on resource-constrained networking).
- [x] Al-Fuqaha, A., et al. (2015). "Internet of Things: A Survey on Enabling Technologies, Protocols, and Applications." IEEE Communications Surveys & Tutorials. (A foundational paper for any IoT thesis).
- [ ] Karagiannis, V., et al. (2015). "A Survey on Mesh Networking in the IoT." Standardization and Research. (Context for why lightweight protocols are necessary).

### II. Data Serialization & Performance (Protobuf vs. JSON)
- [x] Google Developers (2023). Protocol Buffers Documentation. (The primary source for your binary serialization theory).
- [ ] Maeda, K. (2012). "Performance Evaluation of Object Serialization Libraries for XML, JSON and Protocol Buffers." Proceedings of the 2nd International Conference on Digital Information and Communication Technology.
- [x] Sumaray, A., & Makki, S. K. (2012). "A Comparison of Data Serialization Formats for Optimal Efficiency on a Mobile Platform." ACM. (Empirical evidence for Protobuf efficiency).
- [x] Vinoski, S. (2006). "Advanced Message Queuing Protocol." IEEE Internet Computing. (Theoretical background on message-oriented middleware).

### III. System Language & Architecture (Go & Python)
- [ ] Donovan, A. A., & Kernighan, B. W. (2015). The Go Programming Language. Addison-Wesley. (Justifies your choice of Go for concurrency and Goroutines).
- [ ] Pike, R. (2012). "Go at Google: Software Engineering in the Service of Cloud Computing." ACM Queue. (Explains the philosophy of Go's parallel processing).
- [ ] Lutz, M. (2013). Learning Python. O'Reilly Media. (Reference for Service 1 simulation logic).

### IV. Databases & Visualization (InfluxDB & Grafana)
- [x] Naqvi, S. N. R., et al. (2017). "Time Series Databases and InfluxDB." International Journal of Computer Science and Information Security. (Theoretical justification for TSDB over Relational DBs).
- [ ] Bader, A., et al. (2017). "A Comparative Analysis of Time Series Databases." Lecture Notes in Computer Science.
- [x] Challis, K. (2022). Hands-On Dashboard Development with Grafana. Packt Publishing. (Documentation for your visualization layer).

### V. Containerization & Security (Podman)
- [x] Walsh, D. (2019). Podman in Action. Manning Publications. (The definitive source for explaining "rootless" and "daemonless" containerization).
- [ ] Bernstein, D. (2014). "Containers and Cloud: From LinuX Containers to Docker." IEEE Cloud Computing. (Historical context of containerization).
- [x] Pahl, C., & Lee, B. (2015). "Containers and Clusters for Edge Computing." IEEE International Conference on Cloud Computing. (Connects Podman/Docker specifically to the IoT Edge).

### VI. Data Integrity & Validation
- [x] Fowler, M. (2002). Patterns of Enterprise Application Architecture. Addison-Wesley. (The theoretical origin of the "Pipeline" and "Middleware" patterns you are using).
- [ ] Rahm, E., & Do, H. H. (2000). "Data Cleaning: Problems and Current Approaches." IEEE Data Eng. Bull. (Fundamental theory for your validation middleware).

#### Rajmund publikációi
- https://dblp.uni-trier.de/pid/185/0917.html
- https://www.researchgate.net/profile/Rajmund-Drenyovszki

## Melléklet
