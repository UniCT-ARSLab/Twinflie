# digital twin 

Per digital twin si intende un modello informatico che riflette lo stato di un sistema reale, per esempio supponiamo di avere un qualche impianto industriale e di voler monitorare lo stato del sistema al fine di prevedere l'usura e anticipare evenutuali guasti, per prima cosa potremmo usare dei sensori per monitorare lo stato attuale del sistema, ma grazie alle più moderne teconologie è possibile costruire un modello informatico che usando la fisica del mondo in cui viviamo simuli e si comporti esattamente come il sistema reale. In questo modo quello che abbiamo è un vero e proprio gemello digitale,digital twin, del sistema che si sta esaminando, in questo modo simulando sul modello digitale le stesse sollecitazioni che potrebbe avere il sistema reale, possiamo prevedere come si comporterebbe il sistema reale a quelle sollecitazioni, per prevedere guasti etc...

Questo concetto di digital Twin è aplicabile a un moltitudine di campi dal settore automobilistico a settore idustriale fino a un settore consumer.

Per esempio nel caso del settore autobilistico in un futuro una macchina potrebbe avere tramite opportuna sensoristica un modo per capire le sollecitazioni a cui sono sottoposte tutte le sue componenti e potrebbe stimare lo stato di usura di quest'ultima, in questo modo si potrebbero evitare eventuali rotture e diminuire imprevisti e manutenzioni straordinarie.

# simulation (drone and etc..)

Al fine della simulazione verra usato godot che permettera una semplice visualizzazione in un mondo 3d ma volendo si potrebbe fare una simulazione puramente matematica in c/c++ per avere il massimo dell'efficenza, rinunciando alla visualizzazione.

# applicazione mondo reale

oltre la simulazione e la visualizzazione in un mondo virtuale il progetto si propone di poter inviare un percorso ai droni al fine di effetuare lo stesso percorso nel mondo reale.

# state of arts



# my progect 

Il progetto preso in esame si presuppone di realizzare 2 componenti un applicativo in python che si interfaccia direttamente con i droni tramite il protocollo crazyradio e un client in godot che si interfaccia con il server python tramite http e udp.

l'applicativo python permettera di gestire ad alto livello i droni memorizzandone la posizione e l'orientamento, inoltre permettera di farli muovere tramite una funziona di go_to_point. Inoltre gestira un servizio di api che ci faranno interfacciare con i droni, inoltre un client con un'opportuna richiesta si potra iscrivere a un servizio udp che continua a inviare la posizione dei droni circa ogni mezzo secondo.


## a cosa serve

Il progetto serve per monitorare, simulare e controllare uno sciame di droni a distanza, in un ambiente in-door. 

## tecnologie utilizzate
(sistema di localizzazione)

la comunicazione tra i droni e il server python avviena tramite il protocolo crazyradio.

I droni sono dei dei crazyflie 2.0 equipaggiati con il modulo loco positioning che permettono di utilizzare un set di ancore per localizzarsi in un ambiente. 

il sistema di localizzazione che utilizzano i droni è basato su delle ancore posizionate agli angoli della stanza, in particolare i droni utilizzano il tempo di trasmissione del segnale radio per capire a che distanza si trovano da ogni ancora, utilizzando l'informazione della distanza da ogni ancora riescono a triangolare la loro posizione nello spazio.


### struttura interna e funzionamento 

Il server python usa un classe (uav) per interfacciarsi con il drone, gestisce un server flask che accetta richieste http e risponde con dei json, in particolare le richieste che destisce sono /connect_to/url/<url> che prende come parametro l'urs di drone e si connette ad esso, /get_anchor_pos invece se il server è connesso a un drone prende la posizione corrente delle ancore e le da in output in un json. Il server inoltre espone un servizio udp che agiorna i client che si sottoscrivono della posizione in tempo reale di ogni drone.

il client a sua volta permette di connetersi a un nuovo drone tramite un tasto connect,  

## interazione reale - virtuale

### controllo e simulazione

## generazione e avvio del reale



# conclusioni e possibili sviluppi futuri

Gli obbiettivi del progetto (forse) sono stati pienamente raggiunti e si è riusciti a creare un software in grado di simulare il comportamento dei droni usati per questo progetto. Nel futuro sarebbe possibili sare le hololens per visualizzare il simulatore sovrapposto al mondo reale.