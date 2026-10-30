#include "wifi_control_contract.h"

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int hex_digit(char value)
{
    if (value >= '0' && value <= '9') return value - '0';
    if (value >= 'a' && value <= 'f') return value - 'a' + 10;
    return -1;
}

int main(int argc, char **argv)
{
    if (argc != 4) return 2;

    const size_t hex_length = strlen(argv[1]);
    if (hex_length % 2U != 0U || hex_length > 8192U) return 2;
    const size_t byte_count = hex_length / 2U;
    char bytes[4097];

    for (size_t i = 0U; i < byte_count; ++i) {
        const int high = hex_digit(argv[1][2U * i]);
        const int low = hex_digit(argv[1][2U * i + 1U]);
        if (high < 0 || low < 0) return 2;
        bytes[i] = (char)(high * 16 + low);
    }
    bytes[byte_count] = '\0';

    char *end = NULL;
    const unsigned long requested_length = strtoul(argv[2], &end, 10);
    if (end == argv[2] || *end != '\0') return 2;
    const size_t length = (size_t)requested_length;
    if (length > byte_count) return 2;

    wifi_control_request_t output;
    memset(&output, 0xa5, sizeof(output));
    unsigned char before[sizeof(output)];
    memcpy(before, &output, sizeof(output));

    const char *text = strcmp(argv[3], "null_text") == 0 ? NULL : bytes;
    wifi_control_request_t *out = strcmp(argv[3], "null_out") == 0 ? NULL : &output;
    const wifi_control_parse_status_t status = wifi_control_parse(text, length, out);
    const bool unchanged = memcmp(before, &output, sizeof(output)) == 0;

    printf("status=%d unchanged=%d zero_null=%d", (int)status, (int)unchanged,
           (int)wifi_control_zero_only_allows(NULL));

    if (status == WIFI_CONTROL_PARSE_OK) {
        printf(" type=%d boot=%" PRIu32 " request=%" PRIu32
               " control=%" PRIu32 " ticket=%" PRIu32
               " vx=%" PRId32 " w=%" PRId32
               " session=%" PRIu32 " accepted=%" PRIu64 " expires=%" PRIu64
               " zero=%d",
               (int)output.type, output.expected_boot_id, output.request_id,
               output.control_id, output.ticket, output.vx_mmps, output.w_mradps,
               output.ws_session_id, output.accepted_ms, output.expires_ms,
               (int)wifi_control_zero_only_allows(&output));
    }
    putchar('\n');
    return 0;
}
