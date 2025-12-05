#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

char *my_strdup(const char *s) {
    size_t len = strlen(s) + 1;
    char *copy = malloc(len);
    if (!copy) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    memcpy(copy, s, len);
    return copy;
}

typedef struct {
    char *key;
    int value;
} kv_t;

typedef struct {
    kv_t *items;
    size_t size;
    size_t capacity;
} kv_array_t;

void kv_array_init(kv_array_t *arr) {
    arr->items = NULL;
    arr->size = 0;
    arr->capacity = 0;
}

void kv_array_push(kv_array_t *arr, const char *word, int value) {
    if (arr->size == arr->capacity) {
        size_t new_cap = (arr->capacity == 0) ? 128 : arr->capacity * 2;
        kv_t *new_items = realloc(arr->items, new_cap * sizeof(kv_t));
        if (!new_items) {
            perror("realloc");
            exit(EXIT_FAILURE);
        }
        arr->items = new_items;
        arr->capacity = new_cap;
    }
    arr->items[arr->size].key = my_strdup(word);
    arr->items[arr->size].value = value;
    arr->size++;
}

void kv_array_free(kv_array_t *arr) {
    for (size_t i = 0; i < arr->size; ++i) {
        free(arr->items[i].key);
    }
    free(arr->items);
    arr->items = NULL;
    arr->size = arr->capacity = 0;
}

void normalize_word(char *s) {
    char *start = s;
    while (*start && !isalpha((unsigned char)*start)) start++;
    char *end = start + strlen(start);
    while (end > start && !isalpha((unsigned char)*(end - 1))) end--;
    *end = '\0';
    if (start != s)
        memmove(s, start, end - start + 1);
    for (char *p = s; *p; ++p)
        *p = (char)tolower((unsigned char)*p);
}

void map_emit(kv_array_t *intermediate, const char *word) {
    if (word[0] == '\0') return;
    kv_array_push(intermediate, word, 1);
}

void map_file(FILE *fp, kv_array_t *intermediate) {
    char buffer[256];
    while (fscanf(fp, "%255s", buffer) == 1) {
        normalize_word(buffer);
        if (buffer[0] != '\0')
            map_emit(intermediate, buffer);
    }
}

int kv_compare(const void *a, const void *b) {
    const kv_t *ka = (const kv_t *)a;
    const kv_t *kb = (const kv_t *)b;
    return strcmp(ka->key, kb->key);
}

void reduce_and_write(kv_array_t *intermediate, FILE *out) {
    if (intermediate->size == 0) return;
    size_t i = 0;
    while (i < intermediate->size) {
        char *current_key = intermediate->items[i].key;
        int sum = 0;
        while (i < intermediate->size &&
               strcmp(intermediate->items[i].key, current_key) == 0) {
            sum += intermediate->items[i].value;
            i++;
        }
        fprintf(out, "%s %d\n", current_key, sum);
    }
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <input.txt> <output.txt>\n", argv[0]);
        return EXIT_FAILURE;
    }

    FILE *in = fopen(argv[1], "r");
    if (!in) {
        perror("fopen input");
        return EXIT_FAILURE;
    }

    FILE *out = fopen(argv[2], "w");
    if (!out) {
        perror("fopen output");
        fclose(in);
        return EXIT_FAILURE;
    }

    kv_array_t intermediate;
    kv_array_init(&intermediate);

    map_file(in, &intermediate);
    fclose(in);

    qsort(intermediate.items, intermediate.size, sizeof(kv_t), kv_compare);

    reduce_and_write(&intermediate, out);

    fclose(out);
    kv_array_free(&intermediate);

    return EXIT_SUCCESS;
}
