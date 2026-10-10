idf_component_register(
    SRCS "wifi_control_owner.c" "wifi_control_ticket.c"
         "wifi_link_main.c" "wifi_control_contract.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES
        esp_wifi esp_event esp_netif esp_http_server
        esp_timer esp_system esp_hw_support nvs_flash freertos
        esp_driver_uart
)
