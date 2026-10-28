<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Default Hash Driver
    |--------------------------------------------------------------------------
    |
    | laravel-new defaults to argon2id so long passphrases are not silently
    | truncated the way bcrypt is at 72 bytes. Switch back to bcrypt only if
    | you also set BCRYPT_LIMIT (e.g. 72) so over-long values fail closed.
    |
    | Supported: "bcrypt", "argon", "argon2id"
    |
    */

    'driver' => env('HASH_DRIVER', 'argon2id'),

    'bcrypt' => [
        'rounds' => env('BCRYPT_ROUNDS', 12),
        'verify' => env('HASH_VERIFY', true),
        // Fail instead of silently truncating when using bcrypt.
        'limit' => env('BCRYPT_LIMIT', 72),
    ],

    'argon' => [
        'memory' => env('ARGON_MEMORY', 65536),
        'threads' => env('ARGON_THREADS', 1),
        'time' => env('ARGON_TIME', 4),
        'verify' => env('HASH_VERIFY', true),
    ],

    'rehash_on_login' => true,

];
