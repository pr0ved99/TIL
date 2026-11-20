idf_component_register(
    SRCS "http_server_main.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES
        esp_wifi esp_event esp_netif nvs_flash freertos esp_http_server
)