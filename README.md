# ha-airporce
Custom Home Assistant integration for AirPorce air purifiers.

## Install / Update

1. Locate to your Home Assistant installation path (e.g. `/opt/Configs/HomeAssistant`), then run:
    ```bash
    cd custom_components
    wget https://github.com/jackjinke/ha-airporce/archive/refs/heads/main.zip
    unzip main.zip
    rm -rf airporce
    mv ha-airporce-main/custom_components/airporce/ .
    rm -rf ha-airporce-main/
    rm main.zip
    ```

2. Restart Home Assistant (Settings -> System -> Power icon at top-right corner -> Restart Home Assistant)
3. Setup integration (Settings -> Device & Services -> Add integration (bottom-right) -> AirPorce)
