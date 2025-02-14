from pymongo import ASCENDING


class DBIndexes:
    @staticmethod
    def get_indexes(collection_name):
        index_creation_map = {
            "module_versions": [
                "module_name_lc",
                "git_commit_hash",
                [
                    ("module_name_lc", ASCENDING),
                    ("git_commit_hash", ASCENDING),
                    True,
                    False,
                ],
            ],
            "local_functions": [
                "function_id",
                [
                    ("module_name_lc", ASCENDING),
                    ("function_id", ASCENDING),
                    ("git_commit_hash", ASCENDING),
                    True,
                    False,
                ],
                "module_name_lc",
                "git_commit_hash",
                [
                    ("module_name_lc", ASCENDING),
                    ("function_id", ASCENDING),
                    ("git_commit_hash", ASCENDING),
                    True,
                    False,
                ],
            ],
            "developers": [("kb_username", True, False)],
            "build_logs": [
                ("registration_id", True, False),
                "module_name_lc",
                "timestamp",
                "registration",
                "git_url",
                "current_versions.release.release_timestamp",
            ],
            "favorites": [
                "user",
                "module_name_lc",
                "id",
                [
                    ("user", ASCENDING),
                    ("id", ASCENDING),
                    ("module_name_lc", ASCENDING),
                    True,
                    False,
                ],
            ],
            "exec_stats_raw": [
                "user_id",
                [("app_module_name", ASCENDING), ("app_id", ASCENDING), False, True],
                [
                    ("func_module_name", ASCENDING),
                    ("func_name", ASCENDING),
                    False,
                    True,
                ],
                "creation_time",
                "finish_time",
            ],
            "exec_stats_apps": [
                ("module_name", False, True),
                [
                    ("full_app_id", ASCENDING),
                    ("type", ASCENDING),
                    ("time_range", ASCENDING),
                    True,
                    False,
                ],
                [("type", ASCENDING), ("time_range", ASCENDING), False, True],
            ],
            "exec_stats_users": [
                [
                    ("user_id", ASCENDING),
                    ("type", ASCENDING),
                    ("time_range", ASCENDING),
                    True,
                    False,
                ]
            ],
            "client_groups": [
                [
                    ("module_name_lc", ASCENDING),
                    ("function_name", ASCENDING),
                    True,
                    False,
                ]
            ],
            "volume_mounts": [
                [
                    ("client_group", ASCENDING),
                    ("module_name_lc", ASCENDING),
                    ("function_name", ASCENDING),
                    True,
                    False,
                ]
            ],
            "secure_config_params": [
                "module_name_lc",
                [
                    ("module_name_lc", ASCENDING),
                    ("version", ASCENDING),
                    ("param_name", ASCENDING),
                    True,
                    False,
                ],
            ],
        }
        return index_creation_map.get(collection_name, [])
