<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Default Hash Driver
    |--------------------------------------------------------------------------
    |
    | laravel-new defaults to argon2id per OWASP Password Storage Cheat Sheet
    | (first choice; bcrypt is legacy-only). NIST SP 800-63B-4 requires that
    | verifiers SHALL NOT truncate passwords — argon2id hashes the full input.
    |
    | Supported: "bcrypt", "argon", "argon2id"
    |
    */

    'driver' => env('HASH_DRIVER', 'argon2id'),

    'bcrypt' => [
        'rounds' => env('BCRYPT_ROUNDS', 12),
        'verify' => env('HASH_VERIFY', true),
        'limit' => env('BCRYPT_LIMIT', null),
    ],

    /*
    |--------------------------------------------------------------------------
    | Argon2id Options
    |--------------------------------------------------------------------------
    |
    | OWASP minimum for Argon2id: m=19456 KiB (19 MiB), t=2, p=1.
    | Laravel's defaults (65536 KiB / t=4 / p=1) already exceed that floor;
    | we set them explicitly so upgrades stay intentional.
    |
    */

    'argon' => [
        'memory' => env('ARGON_MEMORY', 65536),
        'threads' => env('ARGON_THREADS', 1),
        'time' => env('ARGON_TIME', 4),
        'verify' => env('HASH_VERIFY', true),
    ],

    /*
    |--------------------------------------------------------------------------
    | Rehash On Login
    |--------------------------------------------------------------------------
    |
    | When true, Laravel rehashes on login if the configured algorithm/work
    | factor changed (Hash::needsRehash) — e.g. upgrading stored bcrypt hashes
    | after switching the default driver to argon2id.
    |
    */

    'rehash_on_login' => true,

];
