#! /usr/bin/python

# Sistema di automazione dell'innaffiatura delle piante mediante previa 
# la ricezione di parametri di input da parte di vari sensori di umidità e
# temperatura.
# Scritto da Giovanni Fiore

# la successiva riga mi permette di non sputtanare tutto quando printo
# caratteri accentati

# -*- coding: utf-8 -*-

import time
import os
import RPi.GPIO as GPIO

# silenzio i warnings per i Pin già utilizzati

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# La modalità di DEBUG mi scrive in maniera verbose una serie di log del sistema
DEBUG = 0

# funzione per leggere dall'ADC (canali dallo 0 al 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # il clock parte con pin basso
        GPIO.output(cspin, False)     # il CS parte con pin basso

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout







def downloadFile(url, fileName):
    fp = open(fileName, "wb")
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, fp)
    curl.perform()
    curl.close()
    fp.close()
    
 
def getGoogleSpeechURL(phrase):
    googleTranslateURL = "http://translate.google.com/translate_tts?tl=it&"
    parameters = {'q': phrase}
    data = urllib.urlencode(parameters)
    googleTranslateURL = "%s%s" % (googleTranslateURL,data)
    return googleTranslateURL
 
def speakSpeechFromText(phrase):
    googleSpeechURL = getGoogleSpeechURL(phrase)
    downloadFile(googleSpeechURL,"tts.mp3")
    os.system("mplayer tts.mp3 -af extrastereo=0 &")


# definizione dei 4 pin utilizzati sul pinout di RaspBerry PI 2
# Utilizzo l'interfaccia SPI di RPI2 che è notevolmente piu veloce.

SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8

# Setto tutti i pin come output tranne ovviamente il pin MISO che è un INPUT
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# inizializzazione dei canali di input
sensore_umidita = 0;


ultima_lettura = 0   # ultima lettura dal sensore
tolleranza = 5       # tolleranza per evitare possibili oscillazioni della lettura (5 è il valore di default)

while True:
        # assumiamo per default che il valore dell'umidità non è cambiato all'inizio
        valore_cambiato = False

        # read the analog pin
        valore_umidita = readadc(sensore_umidita, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # quanto è variata l'umidità rispetto all'ultima lettura?
        variazione_umidita = abs(valore_umidita - ultima_lettura)

        if DEBUG:
                print "valore_umidita:", valore_umidita
                print "variazione_umidita:", variazione_umidita
                print "ultima_lettura", ultima_lettura

        # se risulta variata di un valore maggiore della tolleranza, reputo corretta la variazione
        if ( variazione_umidita > tolleranza ):
               valore_cambiato = True

        if DEBUG:
                print "valore cambiato -> ", valore_cambiato

        if ( valore_cambiato ):
                umidita = valore_umidita / 10.24  # converto i 10bit dell'ADC (0-1024) in una lettura percentuale (0-100%)
                umidita = round(umidita)          # arrotondo i decimali...
                umidita = int(umidita)            # ...e faccio un cast per la sua parte intera

                print 'Umid = {stampaumidita}%' .format(stampaumidita = umidita)
                speak = u"Vediamo...: %sDegrees\nUmidità =....{stampaumidita}%" % ("Prova 1", format(stampaumidita = umidita))
                #speakmore =u"The Ambient Temperature is: %sDegrees\nThe Relative Humidity is: %s%%" % (str(dtemp), str(humidity))
                speakSpeechFromText(speak)

                if DEBUG:
                        print "umidita", umidita
                        print "tri_pot_changed", umidita

                # salva il valore dell'ultima lettura per il prossimo giro
                ultima_lettura = valore_umidita

        # aspetto un secondo secondo per rifare la procedura
        time.sleep(1)
