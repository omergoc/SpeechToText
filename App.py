from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import  Qt, QUrl, QSize,QCoreApplication,pyqtSignal, QThread
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLineEdit,
        QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QPlainTextEdit, QStatusBar,QProgressBar,QMessageBox)
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from moviepy.video.io.VideoFileClip import VideoFileClip
from googletrans import Translator
from pytube import YouTube 
import requests
import os
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

        self.trConvert = QPushButton("Türkçe Çeviri ")
        self.trConvert.clicked.connect(self.translateTR)

        self.n = 0
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(400)
        
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
            self.statusBar.showMessage("Video İndiriliyor.")
            self.download = threadDownload(self.youtubeUrl.text())
            self.download.sonuc.connect(self.Finish)
            self.download.start()


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
                QMessageBox.about(self, "Hatalı Video", "MP4 Dosyası Bulunamadı Yada Bozuk.")
                QCoreApplication.quit()

            self.play()


    def videoConvert(self,video):
        self.statusBar.showMessage("Ses Ayıklama İşlemi Başlatıldı.")
        self.ConvertMp3 = threadVideoConvert(video)
        self.ConvertMp3.result.connect(self.jsonCreate)
        self.ConvertMp3.start()
        self.ProgressBar()


    def jsonCreate(self):
        self.statusBar.showMessage("Json Dosyası Oluşturuluyor.")
        self.readJson = threadJsonCreate()
        self.readJson.result.connect(self.jsonRead)
        self.readJson.start()
        self.ProgressBar()


    def jsonRead(self):
        self.statusBar.showMessage("Json Dosyası Okunuyor.")
        self.readJson = threadJsonRead()
        self.readJson.result.connect(self.WriteText)
        self.readJson.start()
        self.ProgressBar()


    def WriteText(self):
        with open("Veri.txt", "r", encoding="utf8") as file:
            text = file.read()
            self.textArea.clear()
            self.textArea.insertPlainText(text)
        self.statusBar.showMessage("İşlem Tamamlandı.")
        self.ProgressBar()


    def translateTR(self):
        try:
            self.statusBar.showMessage("Türkçe Diline Çeviriliyor.")
            self.textArea.clear()
            with open("Veri.txt", "r", encoding="utf8") as file:
                global text
                text = file.read()
            self.createTranslateTR = threadTranslateTR(text)
            self.createTranslateTR.result.connect(self.ProgressBar)
            self.createTranslateTR.start()
            self.WriteText()
        except:
            QMessageBox.about(self, "Hata", "Veri.Txt Dosyası Bulunamadı.")
            QCoreApplication.quit()



    def translateProgress(self):
        for i in range(400):
            time.sleep(0.01)
            self.n  = self.n + 1
            self.progressBar.setValue(self.n)


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


    def ProgressBar(self):
        for i in range(100):
            time.sleep(0.01)
            self.n  = self.n + 1
            self.progressBar.setValue(self.n)


class threadDownload(QThread):
    result = pyqtSignal(object)

    def __init__(self,link):
        super().__init__()
        self.link = link


    def run(self):
        try:
            youtubeDownload = Youtube(self.link)
            youtubeDownload.Download()
            self.result.emit("İşlem Tamamlandı.")
        except:
            self.result.emit("Beklenmedik Bir Hata Oluştu.")


class Youtube():
    def __init__(self,link):
        self.link = link

    def Download(self):
        controlVideo= self.link
        video_url = YouTube(controlVideo)
        videos = video_url.streams.filter(file_extension='mp4').first()
        videos.download()


class threadVideoConvert(QThread):
    result = pyqtSignal(object)

    def __init__(self,video):
        super().__init__()
        self.video = video

    def run(self):
        try:
            videoConvert = VideoConvert(self.video)
            videoConvert.Mp3Convert()
            self.result.emit("İşlem Tamamlandı.")
        except:
            self.result.emit("Beklenmedik Bir Hata Oluştu.")


class VideoConvert():
    
    def __init__(self,video):
        self.video = video
    
    def Mp3Convert(self):
        video = VideoFileClip(os.path.join(self.video))
        video.audio.write_audiofile(os.path.join("ses.mp3"))


class threadJsonCreate(QThread):
    result = pyqtSignal(object)

    def __init__(self):
        super().__init__()
    
    def run(self):
        jsonCreate = DataJson()
        jsonCreate.Create()
        self.result.emit("İşlem Tamamlandı.")

class threadJsonRead(QThread):
    result = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            jsonRead = DataJson()
            jsonRead.Read()
            self.result.emit("İşlem Tamamlandı.")
        except:
            self.result.emit("Beklenmedik Bir Hata Oluştu.")

class DataJson():

    @staticmethod
    def Create():
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
    
    @staticmethod
    def Read():
        with open('data.json', 'r') as openfile:
            x = json.load(openfile)
            array = []
            y = x['results']

            for item in y:
                for item in item['alternatives']:
                    array.append(item['transcript'])

            text = str(array).replace('"',"").replace("[","").replace("]","")

            with open("Veri.txt", "w") as f:
                f.write(text)


class threadTranslateTR(QThread):
    result = pyqtSignal(object)

    def __init__(self,text):
        super().__init__()
        self.text = text


    def run(self):
        try:
            translateConvert = Translate(self.text)
            translateConvert.Tr()
            self.result.emit("İşlem Tamamlandı.")
        except:
            self.result.emit("Beklenmedik Bir Hata Oluştu.")


class Translate():

    def __init__(self,text):
        self.text = text
    
    def Tr(self):

        translator = Translator()
        example = translator.translate(self.text,dest="tr")
        
        with open("Veri.txt","w", encoding="utf8") as file:
            file.write(example.text)



if __name__ == '__main__':
    from sys import argv,exit
    app = QApplication(argv)
    root = App()
    root.setWindowTitle("THT Speech To Text // Beta") 
    root.resize(800, 600)
    root.show()
    exit(app.exec_())



    
