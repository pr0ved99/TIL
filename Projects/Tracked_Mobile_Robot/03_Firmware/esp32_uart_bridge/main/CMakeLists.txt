idf_component_register(SRCS "uart_bridge_main.c"
                       PRIV_REQUIRES esp_driver_uart esp_driver_gpio
                       INCLUDE_DIRS "")
