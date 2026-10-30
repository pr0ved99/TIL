/* HTTP adapters only. The actual handler and test step are extracted from C. */
static const char *mock_http_body;
static size_t mock_http_offset, mock_http_chunk;
static bool mock_http_recv_fail;
static char mock_http_status[32], mock_http_response[96];
static int httpd_req_recv(httpd_req_t *req, char *buffer, size_t length)
{
    (void)req; CHECK(mock_lock_depth == 0U);
    if (mock_http_recv_fail) return -1;
    if (mock_http_chunk && length > mock_http_chunk) length = mock_http_chunk;
    memcpy(buffer, mock_http_body + mock_http_offset, length);
    mock_http_offset += length;
    return (int)length;
}
static esp_err_t httpd_resp_set_status(httpd_req_t *req, const char *status)
{
    (void)req; CHECK(mock_lock_depth == 0U);
    snprintf(mock_http_status, sizeof(mock_http_status), "%s", status);
    return ESP_OK;
}
static esp_err_t httpd_resp_sendstr(httpd_req_t *req, const char *body)
{
    (void)req; CHECK(mock_lock_depth == 0U);
    snprintf(mock_http_response, sizeof(mock_http_response), "%s", body);
    return ESP_OK;
}
