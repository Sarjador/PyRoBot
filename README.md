/PyRoBot/
├── dataset/
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   └── val/
│       ├── images/
│       └── labels/
│
├── models/
│   └── best.pt                        # Modelo entrenado YOLOv8
│
├── core/
│   ├── capture.py                     # Captura de pantalla con MSS
│   ├── detection.py                   # Inferencia con YOLO
│   ├── decision.py                    # Sistema de decisiones del bot (reglas + historial)
│   ├── hud_reader.py                  # Lectura de HP/SP (por OCR, color, etc.)
│   └── actions.py                     # Simulación de teclas o clics (futuro)
│
├── scripts/
│   ├── screenshot_capture.py          # Script de captura de dataset
│   └── yolo_inference.py              # Prueba directa del modelo
│
├── data.yaml                          # Clases YOLO
├── requirements.txt                   # Dependencias
├── main.py                            # Entrypoint principal del bot inteligente
└── README.md





LABEL STUDIO -Docker
docker run -it -p 8080:8080 -v `pwd`/mydata:/label-studio/data heartexlabs/label-studio:latest

LABEL STUDIO -Anaconda
1. conda create --name yolo-env1 python=3.12
2. conda activate yolo-env1
3. pip install label-studio
4. label-studio start

Comando para entrenamiento de Yolo:
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=50 imgsz=640 device=0