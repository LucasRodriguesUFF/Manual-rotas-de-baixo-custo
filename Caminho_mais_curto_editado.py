from qgis.core import (
    QgsProject,
    QgsProcessingFeedback,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsMapLayer,
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
)
import processing

class ShortestPathDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Caminho Mais Curto')
        layout = QVBoxLayout()

        self.lbl_origem = QLabel('Selecione a camada de origem:')
        self.combo_origem = QComboBox()
        self.lbl_destino = QLabel('Selecione a camada de destino:')
        self.combo_destino = QComboBox()
        self.lbl_rotas = QLabel('Selecione a camada de dados viários:')
        self.combo_rotas = QComboBox()
        self.lbl_direcao = QLabel('Campo de direção:')
        self.combo_direcao = QComboBox()
        self.lbl_nome_resultado = QLabel('Nome da camada resultante:')
        self.txt_nome_resultado = QLineEdit()
        self.txt_nome_resultado.setText('Rotas')

        self.btn_executar = QPushButton('Executar')
        self.btn_executar.clicked.connect(self.executar_caminho_mais_curto)

        layout.addWidget(self.lbl_origem)
        layout.addWidget(self.combo_origem)
        layout.addWidget(self.lbl_destino)
        layout.addWidget(self.combo_destino)
        layout.addWidget(self.lbl_rotas)
        layout.addWidget(self.combo_rotas)
        layout.addWidget(self.lbl_direcao)
        layout.addWidget(self.combo_direcao)
        layout.addWidget(self.lbl_nome_resultado)
        layout.addWidget(self.txt_nome_resultado)
        layout.addWidget(self.btn_executar)

        self.setLayout(layout)
        self.populate_combo_camadas()

    def populate_combo_camadas(self):
        project = QgsProject.instance()
        layers = project.mapLayers().values()

        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                self.combo_origem.addItem(layer.name(), layer)
                self.combo_destino.addItem(layer.name(), layer)
                self.combo_rotas.addItem(layer.name(), layer)
                fields = layer.fields()
                for field in fields:
                    if field.name() == 'oneway':
                        self.combo_direcao.addItem(field.name(), field.name())

    def get_start_point_coordinates(self):
        camada_origem = self.combo_origem.currentData()
        if camada_origem:
            crs_transform = QgsCoordinateTransform(
                camada_origem.crs(), QgsProject.instance().crs(), QgsProject.instance()
            )
            features = camada_origem.getFeatures()
            for feat in features:
                geom = feat.geometry()
                if geom:
                    transformed_geom = QgsGeometry(geom)
                    transformed_geom.transform(crs_transform)
                    return transformed_geom.asPoint()

    def executar_caminho_mais_curto(self):
        start_point = self.get_start_point_coordinates()
        camada_destino = self.combo_destino.currentData()
        camada_rotas = self.combo_rotas.currentData()
        campo_direcao = self.combo_direcao.currentText()
        nome_resultado = self.txt_nome_resultado.text()

        params = {
            'INPUT': camada_rotas,
            'START_POINT': QgsGeometry.fromPointXY(start_point),
            'END_POINTS': camada_destino,
            'DIRECTION_FIELD': campo_direcao,
            'OUTPUT': 'memory:' + nome_resultado
        }

        feedback = QgsProcessingFeedback()
        result = processing.run("native:shortestpathpointtolayer", params, feedback=feedback)

        if result and 'OUTPUT' in result:
            caminho_mais_curto = result['OUTPUT']
            QgsProject.instance().addMapLayer(caminho_mais_curto)

dialog = ShortestPathDialog()
dialog.exec_()
