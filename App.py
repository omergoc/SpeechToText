from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import  Qt, QUrl, QSize,QCoreApplication
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLineEdit,
        QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QPlainTextEdit, QStatusBar,QProgressBar,QMessageBox)
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from datetime import timedelta
from moviepy.editor import VideoFileClip
from googletrans import Translator
from pytube import YouTube 
import requests
import os
import re
import time
import json


class App(QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowIcon(QIcon('tht.ico'))
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        btnSize = QSize(16, 16)
        videoWidget = QVideoWidget()

        openButton = QPushButton("Video Seç")   
        openButton.setToolTip("Video Seç")
        # openButton.setStatusTip("Video Seç")
        openButton.setFixedHeight(24)
        openButton.setIconSize(btnSize)
        openButton.setFont(QFont("Noto Sans", 8))
        openButton.setIcon(QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png")))
        openButton.clicked.connect(self.openFile)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        self.youtubeUrl = QLineEdit()
        self.videoDowloand = QPushButton("Video İndir")
        self.videoDowloand.clicked.connect(self.youtubeDownload)

        self.textArea = QPlainTextEdit(self)
        self.textArea.setMaximumHeight(100)

        self.trConvert = QPushButton("Türkçe Çeviri /// Alt Yazı Dosyası Oluştur")
        self.trConvert.clicked.connect(self.translateTR)

        self.n = 500
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(self.n)
        
        layout = QVBoxLayout()
        layout.addWidget(self.youtubeUrl)
        layout.addWidget(self.videoDowloand)
        layout.addWidget(videoWidget)
        layout.addWidget(self.textArea)
        layout.addWidget(self.trConvert)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)
        layout.addWidget(self.progressBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Hazır")

        if self.NetworkControl() != True:
            QMessageBox.about(self, "Hata", "İnternet Bağlantınız Bulunmamaktadır.")
            QCoreApplication.quit()

    def NetworkControl(self):
        r = requests.head("https://www.turkhackteam.org/")
        return r.status_code == 200

    def youtubeDownload(self):
        controlVideo= self.youtubeUrl.text()
        if controlVideo == "":
            self.statusBar.showMessage("Adres Alanı Boş Olamaz")
        else:
            self.statusBar.showMessage("Video İndiriliyor")
            self.run()
            time.sleep(1)
            video_url = YouTube(controlVideo)
            videos = video_url.streams.filter(file_extension='mp4').first()
            videos.download()
            self.statusBar.showMessage("İşlem Tamamlandı")


    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Mp4 Türünde Dosya Seçiniz",
                ".", "Video Dosyası (*.mp4)")
        
        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(fileName)
            try:
                self.videoConvert(fileName)
            except:
                QMessageBox.about(self, "Hata", "Video Dosyası Bulunamadı.")
                QCoreApplication.quit()
            try:
                self.jsonCreate()
            except:
                QMessageBox.about(self, "Hatalı API", "API.TXT Dosyası Bulunamadı Yada Hatalı.")
                QCoreApplication.quit()
            try:
                self.jsonRead()
            except:
                QMessageBox.about(self, "Hata", "data.json Dosyası Bulunamadı.")
                QCoreApplication.quit()
            try:
                self.WriteText()
            except:
                QMessageBox.about(self, "Hata", "Veri.Txt Dosyası Bulunamadı.")
                QCoreApplication.quit()
            self.play()


    def videoConvert(self,video):
        video = VideoFileClip(os.path.join(video))
        self.statusBar.showMessage("Ses Ayıklama İşlemi Yapılıyor")
        time.sleep(1)
        self.run()
        video.audio.write_audiofile(os.path.join("ses.mp3"))


    def jsonCreate(self):
        self.statusBar.showMessage("Json Dosyası Oluşturuluyor")
        time.sleep(1)
        self.run()
        with open("API.txt", "r") as f:
            api_txt = f.read()

        api=IAMAuthenticator(api_txt)
        speech_2_text = SpeechToTextV1(authenticator=api)
        speech_2_text.set_service_url("https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/2b854a53-1b61-4264-bb6c-0ff850bca6f0")

        with open("ses.mp3","rb") as audio_file:
            global result
            result= speech_2_text.recognize(
                audio=audio_file,content_type="audio/mp3"
            ).get_result()

        with open('data.json', 'w') as f:
            json.dump(result, f)


    def jsonRead(self):
        time.sleep(1)
        self.statusBar.showMessage("Json Dosyası Okunuyor")
        self.run()
        with open('data.json', 'r') as openfile:
            self.x = json.load(openfile)
            array = []
            y = self.x['results']

            for item in y:
                for item in item['alternatives']:
                    array.append(item['transcript'])

            text = str(array).replace('"',"").replace("[","").replace("]","")

            with open("Veri.txt", "w") as f:
                f.write(text)


    def WriteText(self):
        time.sleep(1)
        self.statusBar.showMessage("Video Başlatıldı")
        with open("Veri.txt", "r") as file:
            text = file.read()
            self.textArea.clear()
            self.textArea.insertPlainText(text)


    def translateTR(self):
        try:
            time.sleep(1)
            self.statusBar.showMessage("Türkçe Diline Çeviriliyor")
            self.run()
            self.textArea.clear()

            with open("Veri.txt", "r") as file:
                global text
                text = file.read()

            translator = Translator()
            example = translator.translate(text,dest="tr")
            with open("Veri.txt", "w") as f:
                f.write("<font face='Cronos Pro Light' size='8' color='#ff0000'>")
                f.write(example.text)
                f.write("</font>")

            self.TxtToSrt()
            self.textArea.insertPlainText(example.text)
            self.statusBar.showMessage("İşlem Tamamlandı")
            self.progressBar.setValue(0)
        except:
            QMessageBox.about(self, "Hata", "Veri.Txt Dosyası Bulunamadı.")
            QCoreApplication.quit()


    def run(self):
        for i in range(self.n):
            time.sleep(0.01)
            self.progressBar.setValue(i+1)


    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()


    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))


    def positionChanged(self, position):
        self.positionSlider.setValue(position)


    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)


    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)


    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Hata: " + self.mediaPlayer.errorString())


    def createSrt(self):
        with open("altyazi.txt", "w") as f:
            f.write("1")
            f.write("00:00:00,000 --> 0:16:40,000")
            f.write("<font face='Cronos Pro Light' size='8' color='#ff0000'>")
            f.write("</font>")


    def TxtToSrt(self):
        dursec = 1000

        inputtxt = 'Veri.txt'
        subpath = os.path.join(os.path.dirname(__file__), inputtxt)
        subtxt = open(subpath).read()

        par = re.split('\n{2,}', subtxt)

        npar = len(par)

        tdstart = timedelta(hours=0, seconds=-dursec)
        tddur = timedelta(seconds=dursec)

        tdlist = []
        for i in range(npar+1):
            tdstart = tdstart + tddur
            tdlist.append(tdstart)

        lcomb = []
        for i in range(npar):
            lcomb.append(str(i+1) + '\n' + str(tdlist[i]) + ',000 --> ' + str(
                tdlist[i+1]) + ',000' + '\n' + par[i] + '\n')


        srtstring = '\n'.join(lcomb)

        pat = r'^(\d:)'
        repl = '0\\1'
        srtstring2 = re.sub(pat, repl, srtstring, 0, re.MULTILINE)

        srtout = os.path.join(os.path.dirname(__file__), 'altyazi.srt')
        with open(srtout, 'w',encoding="utf-8") as newfile:
            newfile.write(srtstring2)


if __name__ == '__main__':
    from sys import argv,exit
    app = QApplication(argv)
    root = App()
    root.setWindowTitle("THT Speech To Text // Beta") 
    root.resize(800, 600)
    root.show()
    exit(app.exec_())



    
