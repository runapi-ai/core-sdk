CONTRACT = {
    "elevenlabs/isolate-audio": {
        "models": ["audio-isolation"],
        "fields_by_model": {
            "audio-isolation": {}
        }
    },
    "elevenlabs/speech-to-text": {
        "models": ["speech-to-text"],
        "fields_by_model": {
            "speech-to-text": {}
        }
    },
    "elevenlabs/text-to-dialogue": {
        "models": ["text-to-dialogue-v3"],
        "fields_by_model": {
            "text-to-dialogue-v3": {
                "stability": {
                    "enum": [0.0, 0.5, 1.0]
                }
            }
        }
    },
    "elevenlabs/text-to-sound": {
        "models": ["sound-effect-v2"],
        "fields_by_model": {
            "sound-effect-v2": {
                "output_format": {
                    "enum": ["mp3_22050_32", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"]
                }
            }
        }
    },
    "elevenlabs/text-to-speech": {
        "models": ["text-to-speech-multilingual-v2", "text-to-speech-turbo-v2.5"],
        "fields_by_model": {
            "text-to-speech-multilingual-v2": {},
            "text-to-speech-turbo-v2.5": {}
        }
    },
    "fish-audio/text-to-speech": {
        "models": ["s1", "s2-pro", "s2.1-pro"],
        "fields_by_model": {
            "s1": {
                "bitrate_kbps": {
                    "enum": [64, 128, 192]
                },
                "output_format": {
                    "enum": ["mp3", "wav"]
                },
                "sample_rate_hz": {
                    "enum": [8000, 16000, 24000, 32000, 44100]
                }
            },
            "s2-pro": {
                "bitrate_kbps": {
                    "enum": [64, 128, 192]
                },
                "output_format": {
                    "enum": ["mp3", "wav"]
                },
                "sample_rate_hz": {
                    "enum": [8000, 16000, 24000, 32000, 44100]
                }
            },
            "s2.1-pro": {
                "bitrate_kbps": {
                    "enum": [64, 128, 192]
                },
                "output_format": {
                    "enum": ["mp3", "wav"]
                },
                "sample_rate_hz": {
                    "enum": [8000, 16000, 24000, 32000, 44100]
                }
            }
        }
    },
    "flux-2/remix-image": {
        "models": ["flux-2-flex-remix-image", "flux-2-max-remix-image", "flux-2-pro-remix-image"],
        "fields_by_model": {
            "flux-2-flex-remix-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3", "auto"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k"]
                }
            },
            "flux-2-max-remix-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_count": {
                    "enum": [1]
                },
                "output_resolution": {
                    "enum": ["1k"]
                }
            },
            "flux-2-pro-remix-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3", "auto"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k"]
                }
            }
        }
    },
    "flux-2/text-to-image": {
        "models": ["flux-2-flex-text-to-image", "flux-2-max-text-to-image", "flux-2-pro-text-to-image"],
        "fields_by_model": {
            "flux-2-flex-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k"]
                }
            },
            "flux-2-max-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_count": {
                    "enum": [1]
                },
                "output_resolution": {
                    "enum": ["1k"]
                }
            },
            "flux-2-pro-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k"]
                }
            }
        }
    },
    "flux-kontext/text-to-image": {
        "models": ["flux-kontext-max", "flux-kontext-pro"],
        "fields_by_model": {
            "flux-kontext-max": {
                "aspect_ratio": {
                    "enum": ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]
                },
                "output_format": {
                    "enum": ["jpeg", "png"]
                }
            },
            "flux-kontext-pro": {
                "aspect_ratio": {
                    "enum": ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]
                },
                "output_format": {
                    "enum": ["jpeg", "png"]
                }
            }
        }
    },
    "flux/remix-image": {
        "models": ["flux-dev", "flux-pro"],
        "fields_by_model": {
            "flux-dev": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_count": {
                    "enum": [1]
                }
            },
            "flux-pro": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_count": {
                    "enum": [1]
                }
            }
        }
    },
    "flux/text-to-image": {
        "models": ["flux-2-klein", "flux-dev", "flux-pro"],
        "fields_by_model": {
            "flux-2-klein": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_count": {
                    "enum": [1]
                }
            },
            "flux-dev": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_count": {
                    "enum": [1]
                }
            },
            "flux-pro": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_count": {
                    "enum": [1]
                }
            }
        }
    },
    "gemini-omni/create-audio": {
        "models": ["gemini-omni-audio"],
        "fields_by_model": {
            "gemini-omni-audio": {}
        }
    },
    "gemini-omni/create-character": {
        "models": ["gemini-omni-character"],
        "fields_by_model": {
            "gemini-omni-character": {}
        }
    },
    "gemini-omni/text-to-video": {
        "models": ["gemini-omni-flash-preview", "gemini-omni-text-to-video"],
        "fields_by_model": {
            "gemini-omni-flash-preview": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16"]
                },
                "output_resolution": {
                    "enum": ["720p"]
                }
            },
            "gemini-omni-text-to-video": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16"]
                },
                "duration_seconds": {
                    "enum": [4, 6, 8, 10]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p", "4k"]
                }
            }
        }
    },
    "gemini-tts/text-to-speech": {
        "models": ["gemini-2.5-pro-tts", "gemini-3.1-flash-tts"],
        "fields_by_model": {
            "gemini-2.5-pro-tts": {},
            "gemini-3.1-flash-tts": {}
        }
    },
    "gpt-4o-image/text-to-image": {
        "models": ["gpt-4o-image"],
        "fields_by_model": {
            "gpt-4o-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:2", "2:3"]
                },
                "output_count": {
                    "enum": [1, 2, 4]
                }
            }
        }
    },
    "gpt-image-2/edit-image": {
        "models": ["gpt-image-2"],
        "fields_by_model": {
            "gpt-image-2": {
                "aspect_ratio": {
                    "enum": ["auto", "1:1", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5", "16:9", "9:16", "2:1", "1:2", "3:1", "1:3", "21:9", "9:21"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k", "4k"]
                }
            }
        }
    },
    "gpt-image-2/text-to-image": {
        "models": ["gpt-image-2"],
        "fields_by_model": {
            "gpt-image-2": {
                "aspect_ratio": {
                    "enum": ["auto", "1:1", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5", "16:9", "9:16", "2:1", "1:2", "3:1", "1:3", "21:9", "9:21"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k", "4k"]
                }
            }
        }
    },
    "gpt-image/edit-image": {
        "models": ["gpt-image-1.5"],
        "fields_by_model": {
            "gpt-image-1.5": {
                "aspect_ratio": {
                    "enum": ["1:1", "2:3", "3:2"]
                },
                "quality": {
                    "enum": ["medium", "high"]
                }
            }
        }
    },
    "gpt-image/text-to-image": {
        "models": ["gpt-image-1.5"],
        "fields_by_model": {
            "gpt-image-1.5": {
                "aspect_ratio": {
                    "enum": ["1:1", "2:3", "3:2"]
                },
                "quality": {
                    "enum": ["medium", "high"]
                }
            }
        }
    },
    "grok-imagine/edit-image": {
        "models": ["grok-imagine-edit-image"],
        "fields_by_model": {
            "grok-imagine-edit-image": {}
        }
    },
    "grok-imagine/extend": {
        "models": [],
        "fields_by_model": {
            "_": {
                "extension_duration_seconds": {
                    "enum": [6, 10]
                }
            }
        }
    },
    "grok-imagine/image-to-video": {
        "models": ["grok-imagine-image-to-video", "grok-imagine-video-1.5-fast", "grok-imagine-video-1.5-preview"],
        "fields_by_model": {
            "grok-imagine-image-to-video": {
                "aspect_ratio": {
                    "enum": ["2:3", "3:2", "1:1", "16:9", "9:16"]
                },
                "motion_style": {
                    "enum": ["fun", "normal", "spicy"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p"]
                }
            },
            "grok-imagine-video-1.5-fast": {
                "aspect_ratio": {
                    "enum": ["1:1", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p"]
                }
            },
            "grok-imagine-video-1.5-preview": {
                "aspect_ratio": {
                    "enum": ["1:1", "16:9", "9:16", "3:2", "2:3", "auto"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p", "1080p"]
                }
            }
        }
    },
    "grok-imagine/text-to-image": {
        "models": ["grok-imagine-text-to-image"],
        "fields_by_model": {
            "grok-imagine-text-to-image": {
                "aspect_ratio": {
                    "enum": ["2:3", "3:2", "1:1", "16:9", "9:16"]
                }
            }
        }
    },
    "grok-imagine/text-to-video": {
        "models": ["grok-imagine-text-to-video", "grok-imagine-video-1.5-fast", "grok-imagine-video-1.5-preview"],
        "fields_by_model": {
            "grok-imagine-text-to-video": {
                "aspect_ratio": {
                    "enum": ["2:3", "3:2", "1:1", "16:9", "9:16"]
                },
                "motion_style": {
                    "enum": ["fun", "normal", "spicy"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p"]
                }
            },
            "grok-imagine-video-1.5-fast": {
                "aspect_ratio": {
                    "enum": ["1:1", "16:9", "9:16", "3:2", "2:3"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p"]
                }
            },
            "grok-imagine-video-1.5-preview": {
                "aspect_ratio": {
                    "enum": ["1:1", "16:9", "9:16", "3:2", "2:3", "auto"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p", "1080p"]
                }
            }
        }
    },
    "grok-imagine/upscale-image": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "hailuo/image-to-video": {
        "models": ["hailuo-02-image-to-video-pro", "hailuo-02-image-to-video-standard", "hailuo-2.3-image-to-video-pro", "hailuo-2.3-image-to-video-standard"],
        "fields_by_model": {
            "hailuo-02-image-to-video-pro": {},
            "hailuo-02-image-to-video-standard": {
                "duration_seconds": {
                    "enum": [6, 10]
                },
                "output_resolution": {
                    "enum": ["512p", "768p"]
                }
            },
            "hailuo-2.3-image-to-video-pro": {
                "duration_seconds": {
                    "enum": [6, 10]
                },
                "output_resolution": {
                    "enum": ["768p", "1080p"]
                }
            },
            "hailuo-2.3-image-to-video-standard": {
                "duration_seconds": {
                    "enum": [6, 10]
                },
                "output_resolution": {
                    "enum": ["768p", "1080p"]
                }
            }
        }
    },
    "hailuo/text-to-video": {
        "models": ["hailuo-02-text-to-video-pro", "hailuo-02-text-to-video-standard"],
        "fields_by_model": {
            "hailuo-02-text-to-video-pro": {},
            "hailuo-02-text-to-video-standard": {
                "duration_seconds": {
                    "enum": [6, 10]
                }
            }
        }
    },
    "happyhorse/edit-video": {
        "models": ["happyhorse-edit-video"],
        "fields_by_model": {
            "happyhorse-edit-video": {
                "audio_setting": {
                    "enum": ["auto", "original"]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "happyhorse/image-to-video": {
        "models": ["happyhorse-1.0-i2v", "happyhorse-image-to-video"],
        "fields_by_model": {
            "happyhorse-1.0-i2v": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "happyhorse-image-to-video": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "happyhorse/text-to-video": {
        "models": ["happyhorse-1.0-r2v", "happyhorse-1.0-t2v", "happyhorse-character", "happyhorse-text-to-video"],
        "fields_by_model": {
            "happyhorse-1.0-r2v": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "happyhorse-1.0-t2v": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "happyhorse-character": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "happyhorse-text-to-video": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "ideogram-v3/edit-image": {
        "models": ["ideogram-v3-character-edit", "ideogram-v3-edit"],
        "fields_by_model": {
            "ideogram-v3-character-edit": {
                "output_count": {
                    "enum": [1, 2, 3, 4]
                },
                "rendering_speed": {
                    "enum": ["turbo", "balanced", "quality"]
                },
                "style": {
                    "enum": ["auto", "realistic", "fiction"]
                }
            },
            "ideogram-v3-edit": {
                "output_count": {
                    "enum": [1, 2, 3, 4]
                },
                "rendering_speed": {
                    "enum": ["turbo", "balanced", "quality"]
                }
            }
        }
    },
    "ideogram-v3/reframe-image": {
        "models": ["ideogram-v3-reframe"],
        "fields_by_model": {
            "ideogram-v3-reframe": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:4", "9:16", "4:3", "16:9"]
                },
                "output_count": {
                    "enum": [1, 2, 3, 4]
                },
                "rendering_speed": {
                    "enum": ["turbo", "balanced", "quality"]
                },
                "style": {
                    "enum": ["auto", "general", "realistic", "design"]
                }
            }
        }
    },
    "ideogram-v3/remix-image": {
        "models": ["ideogram-v3-character-remix", "ideogram-v3-remix"],
        "fields_by_model": {
            "ideogram-v3-character-remix": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:4", "9:16", "4:3", "16:9"]
                },
                "output_count": {
                    "enum": [1, 2, 3, 4]
                },
                "rendering_speed": {
                    "enum": ["turbo", "balanced", "quality"]
                },
                "style": {
                    "enum": ["auto", "realistic", "fiction"]
                }
            },
            "ideogram-v3-remix": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:4", "9:16", "4:3", "16:9"]
                },
                "output_count": {
                    "enum": [1, 2, 3, 4]
                },
                "rendering_speed": {
                    "enum": ["turbo", "balanced", "quality"]
                },
                "style": {
                    "enum": ["auto", "general", "realistic", "design"]
                }
            }
        }
    },
    "ideogram-v3/text-to-image": {
        "models": ["ideogram-v3-character", "ideogram-v3-text-to-image"],
        "fields_by_model": {
            "ideogram-v3-character": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:4", "9:16", "4:3", "16:9"]
                },
                "output_count": {
                    "enum": [1, 2, 3, 4]
                },
                "rendering_speed": {
                    "enum": ["turbo", "balanced", "quality"]
                },
                "style": {
                    "enum": ["auto", "realistic", "fiction"]
                }
            },
            "ideogram-v3-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:4", "9:16", "4:3", "16:9"]
                },
                "output_count": {
                    "enum": [1, 2, 3, 4]
                },
                "rendering_speed": {
                    "enum": ["turbo", "balanced", "quality"]
                },
                "style": {
                    "enum": ["auto", "general", "realistic", "design"]
                }
            }
        }
    },
    "imagen-4/remix-image": {
        "models": ["imagen-4-pro-remix-image"],
        "fields_by_model": {
            "imagen-4-pro-remix-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "auto"]
                },
                "output_format": {
                    "enum": ["png", "jpg"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k", "4k"]
                }
            }
        }
    },
    "imagen-4/text-to-image": {
        "models": ["imagen-4", "imagen-4-fast", "imagen-4-ultra"],
        "fields_by_model": {
            "imagen-4": {
                "aspect_ratio": {
                    "enum": ["1:1", "16:9", "9:16", "3:4", "4:3"]
                }
            },
            "imagen-4-fast": {
                "aspect_ratio": {
                    "enum": ["1:1", "16:9", "9:16", "3:4", "4:3", "auto"]
                }
            },
            "imagen-4-ultra": {
                "aspect_ratio": {
                    "enum": ["1:1", "16:9", "9:16", "3:4", "4:3"]
                }
            }
        }
    },
    "infinitetalk/audio-to-video": {
        "models": ["infinitetalk-from-audio"],
        "fields_by_model": {
            "infinitetalk-from-audio": {
                "output_resolution": {
                    "enum": ["480p", "720p"]
                }
            }
        }
    },
    "kling/avatar": {
        "models": ["kling-ai-avatar-pro", "kling-ai-avatar-standard", "kling-ai-avatar-v1-pro", "kling-v1-avatar-standard"],
        "fields_by_model": {
            "kling-ai-avatar-pro": {},
            "kling-ai-avatar-standard": {},
            "kling-ai-avatar-v1-pro": {},
            "kling-v1-avatar-standard": {}
        }
    },
    "kling/extend-video": {
        "models": ["kling-v2.5-turbo-image-to-video-pro", "kling-v2.5-turbo-text-to-video-pro"],
        "fields_by_model": {
            "kling-v2.5-turbo-image-to-video-pro": {
                "mode": {
                    "enum": ["std", "pro"]
                }
            },
            "kling-v2.5-turbo-text-to-video-pro": {
                "mode": {
                    "enum": ["std", "pro"]
                }
            }
        }
    },
    "kling/image-to-video": {
        "models": ["kling-o1", "kling-v2.1-master-image-to-video", "kling-v2.1-pro", "kling-v2.1-standard", "kling-v2.5-turbo-image-to-video-pro", "kling-v2.6", "kling-v3-omni", "kling-v3-turbo-image-to-video"],
        "fields_by_model": {
            "kling-o1": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [5]
                },
                "mode": {
                    "enum": ["std", "pro"]
                },
                "reference_video_type": {
                    "enum": ["base", "feature"]
                }
            },
            "kling-v2.1-master-image-to-video": {
                "duration_seconds": {
                    "enum": [5, 10]
                }
            },
            "kling-v2.1-pro": {
                "duration_seconds": {
                    "enum": [5, 10]
                }
            },
            "kling-v2.1-standard": {
                "duration_seconds": {
                    "enum": [5, 10]
                }
            },
            "kling-v2.5-turbo-image-to-video-pro": {
                "duration_seconds": {
                    "enum": [5, 10]
                }
            },
            "kling-v2.6": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [5, 10]
                },
                "mode": {
                    "enum": ["std", "pro"]
                }
            },
            "kling-v3-omni": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p", "4k"]
                }
            },
            "kling-v3-turbo-image-to-video": {
                "duration_seconds": {
                    "enum": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "kling/motion-control": {
        "models": ["kling-3.0", "kling-v2.6"],
        "fields_by_model": {
            "kling-3.0": {
                "background_source": {
                    "enum": ["video", "image"]
                },
                "character_orientation": {
                    "enum": ["video", "image"]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "kling-v2.6": {
                "character_orientation": {
                    "enum": ["video", "image"]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "kling/text-to-video": {
        "models": ["kling-3.0", "kling-o1", "kling-v2.1-master-text-to-video", "kling-v2.5-turbo-text-to-video-pro", "kling-v2.6", "kling-v3-omni", "kling-v3-turbo-text-to-video"],
        "fields_by_model": {
            "kling-3.0": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p", "4k"]
                }
            },
            "kling-o1": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [5]
                },
                "mode": {
                    "enum": ["std", "pro"]
                },
                "reference_video_type": {
                    "enum": ["base", "feature"]
                }
            },
            "kling-v2.1-master-text-to-video": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [5, 10]
                }
            },
            "kling-v2.5-turbo-text-to-video-pro": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [5, 10]
                }
            },
            "kling-v2.6": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [5, 10]
                },
                "mode": {
                    "enum": ["std", "pro"]
                }
            },
            "kling-v3-omni": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p", "4k"]
                }
            },
            "kling-v3-turbo-text-to-video": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1"]
                },
                "duration_seconds": {
                    "enum": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "luma/modify-video": {
        "models": ["luma-modify-video"],
        "fields_by_model": {
            "luma-modify-video": {}
        }
    },
    "midjourney/edit-image": {
        "models": ["midjourney-edit-image"],
        "fields_by_model": {
            "midjourney-edit-image": {}
        }
    },
    "midjourney/extend-video": {
        "models": ["midjourney-image-to-video"],
        "fields_by_model": {
            "midjourney-image-to-video": {}
        }
    },
    "midjourney/get-seed": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "midjourney/image-to-prompt": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "midjourney/image-to-video": {
        "models": ["midjourney-image-to-video"],
        "fields_by_model": {
            "midjourney-image-to-video": {
                "output_resolution": {
                    "enum": ["480p"]
                }
            }
        }
    },
    "midjourney/shorten-prompt": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "midjourney/text-to-image": {
        "models": ["midjourney-v8.1"],
        "fields_by_model": {
            "midjourney-v8.1": {}
        }
    },
    "minimax-h3/image-to-video": {
        "models": ["minimax-h3"],
        "fields_by_model": {
            "minimax-h3": {
                "duration_seconds": {
                    "enum": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                },
                "output_resolution": {
                    "enum": ["768p", "2k"]
                }
            }
        }
    },
    "minimax-h3/text-to-video": {
        "models": ["minimax-h3"],
        "fields_by_model": {
            "minimax-h3": {
                "aspect_ratio": {
                    "enum": ["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]
                },
                "duration_seconds": {
                    "enum": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                },
                "output_resolution": {
                    "enum": ["768p", "2k"]
                }
            }
        }
    },
    "nano-banana/edit-image": {
        "models": ["nano-banana-2-lite", "nano-banana-edit"],
        "fields_by_model": {
            "nano-banana-2-lite": {
                "aspect_ratio": {
                    "enum": ["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "auto"]
                }
            },
            "nano-banana-edit": {
                "aspect_ratio": {
                    "enum": ["1:1", "9:16", "16:9", "3:4", "4:3", "3:2", "2:3", "5:4", "4:5", "21:9", "auto"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                }
            }
        }
    },
    "nano-banana/text-to-image": {
        "models": ["nano-banana", "nano-banana-2", "nano-banana-2-lite", "nano-banana-pro"],
        "fields_by_model": {
            "nano-banana": {
                "aspect_ratio": {
                    "enum": ["1:1", "9:16", "16:9", "3:4", "4:3", "3:2", "2:3", "5:4", "4:5", "21:9", "auto"]
                },
                "output_format": {
                    "enum": ["png", "jpeg", "jpg"]
                }
            },
            "nano-banana-2": {
                "aspect_ratio": {
                    "enum": ["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "auto"]
                },
                "output_format": {
                    "enum": ["png", "jpeg", "jpg"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k", "4k"]
                }
            },
            "nano-banana-2-lite": {
                "aspect_ratio": {
                    "enum": ["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "auto"]
                }
            },
            "nano-banana-pro": {
                "aspect_ratio": {
                    "enum": ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "auto"]
                },
                "output_format": {
                    "enum": ["png", "jpeg", "jpg"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k", "4k"]
                }
            }
        }
    },
    "omnihuman/audio-to-video": {
        "models": ["omnihuman-1.5"],
        "fields_by_model": {
            "omnihuman-1.5": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "omnihuman/human-identification": {
        "models": ["omnihuman-1.5-human-identification"],
        "fields_by_model": {
            "omnihuman-1.5-human-identification": {}
        }
    },
    "omnihuman/subject-detection": {
        "models": ["omnihuman-1.5-subject-detection"],
        "fields_by_model": {
            "omnihuman-1.5-subject-detection": {}
        }
    },
    "openai-transcription/speech-to-text": {
        "models": ["gpt-transcribe", "whisper-1"],
        "fields_by_model": {
            "gpt-transcribe": {
                "model": {
                    "enum": ["gpt-transcribe"]
                },
                "response_format": {
                    "enum": ["json", "text"]
                }
            },
            "whisper-1": {
                "model": {
                    "enum": ["whisper-1"]
                },
                "response_format": {
                    "enum": ["json", "text", "srt", "verbose_json", "vtt"]
                }
            }
        }
    },
    "openai-tts/text-to-speech": {
        "models": ["tts-1", "tts-1-hd"],
        "fields_by_model": {
            "tts-1": {},
            "tts-1-hd": {}
        }
    },
    "pixverse/edit-video": {
        "models": ["pixverse-v6"],
        "fields_by_model": {
            "pixverse-v6": {
                "aspect_ratio": {
                    "enum": ["16:9", "4:3", "1:1", "3:4", "9:16", "2:3", "3:2", "21:9"]
                },
                "enable_audio": {
                    "enum": [True, False]
                },
                "output_resolution": {
                    "enum": ["360p", "540p", "720p", "1080p"]
                }
            }
        }
    },
    "pixverse/extend-video": {
        "models": ["pixverse-v6"],
        "fields_by_model": {
            "pixverse-v6": {
                "enable_audio": {
                    "enum": [True, False]
                },
                "output_resolution": {
                    "enum": ["360p", "540p", "720p", "1080p"]
                }
            }
        }
    },
    "pixverse/image-to-video": {
        "models": ["pixverse-v6"],
        "fields_by_model": {
            "pixverse-v6": {
                "enable_audio": {
                    "enum": [True, False]
                },
                "output_resolution": {
                    "enum": ["360p", "540p", "720p", "1080p"]
                }
            }
        }
    },
    "pixverse/text-to-video": {
        "models": ["pixverse-v6"],
        "fields_by_model": {
            "pixverse-v6": {
                "aspect_ratio": {
                    "enum": ["16:9", "4:3", "1:1", "3:4", "9:16", "2:3", "3:2", "21:9"]
                },
                "enable_audio": {
                    "enum": [True, False]
                },
                "output_resolution": {
                    "enum": ["360p", "540p", "720p", "1080p"]
                }
            }
        }
    },
    "pixverse/transition-video": {
        "models": ["pixverse-v6"],
        "fields_by_model": {
            "pixverse-v6": {
                "enable_audio": {
                    "enum": [True, False]
                },
                "output_resolution": {
                    "enum": ["360p", "540p", "720p", "1080p"]
                }
            }
        }
    },
    "producer/text-to-music": {
        "models": ["fuzz-0.8", "fuzz-1.0", "fuzz-1.0-pro", "fuzz-1.1", "fuzz-1.1-pro", "fuzz-2.0", "fuzz-2.0-pro", "fuzz-2.0-raw"],
        "fields_by_model": {
            "fuzz-0.8": {
                "vocal_mode": {
                    "enum": ["exact_lyrics", "instrumental"]
                }
            },
            "fuzz-1.0": {
                "vocal_mode": {
                    "enum": ["exact_lyrics", "instrumental"]
                }
            },
            "fuzz-1.0-pro": {
                "vocal_mode": {
                    "enum": ["exact_lyrics", "instrumental"]
                }
            },
            "fuzz-1.1": {
                "vocal_mode": {
                    "enum": ["exact_lyrics", "instrumental"]
                }
            },
            "fuzz-1.1-pro": {
                "vocal_mode": {
                    "enum": ["exact_lyrics", "instrumental"]
                }
            },
            "fuzz-2.0": {
                "vocal_mode": {
                    "enum": ["exact_lyrics", "instrumental"]
                }
            },
            "fuzz-2.0-pro": {
                "vocal_mode": {
                    "enum": ["exact_lyrics", "instrumental"]
                }
            },
            "fuzz-2.0-raw": {
                "vocal_mode": {
                    "enum": ["exact_lyrics", "instrumental"]
                }
            }
        }
    },
    "qwen-2/edit-image": {
        "models": ["qwen-2-edit-image"],
        "fields_by_model": {
            "qwen-2-edit-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9", "21:9"]
                },
                "output_format": {
                    "enum": ["jpeg", "png"]
                }
            }
        }
    },
    "qwen-2/text-to-image": {
        "models": ["qwen-2-text-to-image"],
        "fields_by_model": {
            "qwen-2-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:4", "4:3", "9:16", "16:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                }
            }
        }
    },
    "qwen-3/edit-image": {
        "models": ["qwen-3-edit-image", "qwen-3-pro-edit-image"],
        "fields_by_model": {
            "qwen-3-edit-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "21:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k"]
                }
            },
            "qwen-3-pro-edit-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "21:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k"]
                }
            }
        }
    },
    "qwen-3/text-to-image": {
        "models": ["qwen-3-pro-text-to-image", "qwen-3-text-to-image"],
        "fields_by_model": {
            "qwen-3-pro-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "21:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k"]
                }
            },
            "qwen-3-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "21:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k"]
                }
            }
        }
    },
    "qwen-image/edit-image": {
        "models": ["qwen-image-edit-image"],
        "fields_by_model": {
            "qwen-image-edit-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:4", "9:16", "4:3", "16:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                }
            }
        }
    },
    "qwen-image/remix-image": {
        "models": ["qwen-image-remix-image"],
        "fields_by_model": {
            "qwen-image-remix-image": {
                "output_format": {
                    "enum": ["png", "jpeg"]
                }
            }
        }
    },
    "qwen-image/text-to-image": {
        "models": ["qwen-image-text-to-image"],
        "fields_by_model": {
            "qwen-image-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "3:4", "9:16", "4:3", "16:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                }
            }
        }
    },
    "recraft/remove-background": {
        "models": ["recraft-remove-background"],
        "fields_by_model": {
            "recraft-remove-background": {}
        }
    },
    "recraft/upscale-image": {
        "models": ["recraft-crisp-upscale"],
        "fields_by_model": {
            "recraft-crisp-upscale": {}
        }
    },
    "runway-aleph/edit-video": {
        "models": ["runway-aleph"],
        "fields_by_model": {
            "runway-aleph": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "4:3", "3:4", "1:1", "21:9"]
                }
            }
        }
    },
    "runway/extend-video": {
        "models": ["runway"],
        "fields_by_model": {
            "runway": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "runway/text-to-video": {
        "models": ["runway"],
        "fields_by_model": {
            "runway": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"]
                },
                "duration_seconds": {
                    "enum": [5, 10]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "seedance/text-to-video": {
        "models": ["seedance-1.5-pro", "seedance-2-mini", "seedance-2.0", "seedance-2.0-fast", "seedance-2.5", "seedance-v1-pro", "seedance-v1-pro-fast"],
        "fields_by_model": {
            "seedance-1.5-pro": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "21:9"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p", "1080p"]
                }
            },
            "seedance-2-mini": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "21:9", "auto"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p"]
                }
            },
            "seedance-2.0": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "21:9", "auto"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p", "1080p", "4k"]
                }
            },
            "seedance-2.0-fast": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "21:9", "auto"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p"]
                }
            },
            "seedance-2.5": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "21:9", "auto"]
                },
                "duration_seconds": {
                    "enum": [-1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
                },
                "output_format": {
                    "enum": ["mp4", "mov"]
                },
                "output_resolution": {
                    "enum": ["480p", "720p"]
                }
            },
            "seedance-v1-pro": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "21:9"]
                },
                "duration_seconds": {
                    "enum": [5, 10]
                },
                "output_resolution": {
                    "enum": ["480p", "720p", "1080p"]
                }
            },
            "seedance-v1-pro-fast": {
                "duration_seconds": {
                    "enum": [5, 10]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "seedream/decompose-layers": {
        "models": ["seedream-5-pro-layer-decomposition"],
        "fields_by_model": {
            "seedream-5-pro-layer-decomposition": {
                "output_format": {
                    "enum": ["png", "jpeg"]
                },
                "size": {
                    "enum": ["auto", "1K", "1.5K", "2K"]
                }
            }
        }
    },
    "seedream/edit-image": {
        "models": ["seedream-4.5-edit", "seedream-5-lite-edit", "seedream-5-pro-edit", "seedream-v4-edit"],
        "fields_by_model": {
            "seedream-4.5-edit": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "2:3", "3:2", "21:9"]
                },
                "output_quality": {
                    "enum": ["basic", "high"]
                }
            },
            "seedream-5-lite-edit": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "2:3", "3:2", "21:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                },
                "output_quality": {
                    "enum": ["basic", "high", "ultra"]
                }
            },
            "seedream-5-pro-edit": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "2:3", "3:2", "21:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                },
                "output_quality": {
                    "enum": ["basic", "high"]
                }
            },
            "seedream-v4-edit": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "3:2", "2:3", "16:9", "9:16", "21:9"]
                },
                "output_count": {
                    "enum": [1, 2, 3, 4, 5, 6]
                },
                "output_resolution": {
                    "enum": ["1k", "2k", "4k"]
                }
            }
        }
    },
    "seedream/text-to-image": {
        "models": ["seedream-4.5-text-to-image", "seedream-5-lite-text-to-image", "seedream-5-pro-text-to-image", "seedream-v4-text-to-image"],
        "fields_by_model": {
            "seedream-4.5-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "2:3", "3:2", "21:9"]
                },
                "output_quality": {
                    "enum": ["basic", "high"]
                }
            },
            "seedream-5-lite-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "2:3", "3:2", "21:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                },
                "output_quality": {
                    "enum": ["basic", "high", "ultra"]
                }
            },
            "seedream-5-pro-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16", "2:3", "3:2", "21:9"]
                },
                "output_format": {
                    "enum": ["png", "jpeg"]
                },
                "output_quality": {
                    "enum": ["basic", "high"]
                }
            },
            "seedream-v4-text-to-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "3:2", "2:3", "16:9", "9:16", "21:9"]
                },
                "output_count": {
                    "enum": [1, 2, 3, 4, 5, 6]
                },
                "output_resolution": {
                    "enum": ["1k", "2k", "4k"]
                }
            }
        }
    },
    "suno/add-instrumental": {
        "models": ["suno-v4.5-plus", "suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v4.5-plus": {
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            },
            "suno-v5": {
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            },
            "suno-v5.5": {
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            }
        }
    },
    "suno/add-samples": {
        "models": ["suno-v4", "suno-v4.5", "suno-v4.5-plus", "suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v4": {},
            "suno-v4.5": {},
            "suno-v4.5-plus": {},
            "suno-v5": {},
            "suno-v5.5": {}
        }
    },
    "suno/add-vocals": {
        "models": ["suno-v4.5-plus", "suno-v5"],
        "fields_by_model": {
            "suno-v4.5-plus": {
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            },
            "suno-v5": {
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            }
        }
    },
    "suno/blend-lyrics": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/boost-style": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/check-voice": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/convert-audio": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/cover-audio": {
        "models": ["suno-v4", "suno-v4.5", "suno-v4.5-all", "suno-v4.5-plus", "suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v4": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v4.5": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v4.5-all": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v4.5-plus": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v5": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v5.5": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            }
        }
    },
    "suno/create-mashup": {
        "models": ["suno-v4", "suno-v4.5", "suno-v4.5-all", "suno-v4.5-plus", "suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v4": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v4.5": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v4.5-all": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v4.5-plus": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v5": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v5.5": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            }
        }
    },
    "suno/extend-music": {
        "models": ["suno-v4", "suno-v4.5", "suno-v4.5-all", "suno-v4.5-plus", "suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v4": {
                "parameter_mode": {
                    "enum": ["source", "custom"]
                },
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            },
            "suno-v4.5": {
                "parameter_mode": {
                    "enum": ["source", "custom"]
                },
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            },
            "suno-v4.5-all": {
                "parameter_mode": {
                    "enum": ["source", "custom"]
                },
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            },
            "suno-v4.5-plus": {
                "parameter_mode": {
                    "enum": ["source", "custom"]
                },
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            },
            "suno-v5": {
                "parameter_mode": {
                    "enum": ["source", "custom"]
                },
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            },
            "suno-v5.5": {
                "parameter_mode": {
                    "enum": ["source", "custom"]
                },
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                }
            }
        }
    },
    "suno/generate-artwork": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/generate-lyrics": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/generate-midi": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/generate-persona": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/generate-voice": {
        "models": [],
        "fields_by_model": {
            "_": {
                "singer_skill_level": {
                    "enum": ["beginner", "intermediate", "advanced", "professional"]
                }
            }
        }
    },
    "suno/get-timestamped-lyrics": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/inspire-music": {
        "models": ["suno-v4", "suno-v4.5", "suno-v4.5-plus", "suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v4": {},
            "suno-v4.5": {},
            "suno-v4.5-plus": {},
            "suno-v5": {},
            "suno-v5.5": {}
        }
    },
    "suno/regenerate-validation-phrase": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/remaster-audio": {
        "models": ["suno-v4", "suno-v4.5", "suno-v4.5-plus", "suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v4": {},
            "suno-v4.5": {},
            "suno-v4.5-plus": {},
            "suno-v5": {},
            "suno-v5.5": {}
        }
    },
    "suno/replace-section": {
        "models": [],
        "fields_by_model": {
            "_": {
                "model": {
                    "enum": ["suno-v4", "suno-v4.5", "suno-v4.5-all", "suno-v4.5-plus", "suno-v5", "suno-v5.5"]
                }
            }
        }
    },
    "suno/separate-audio-stems": {
        "models": [],
        "fields_by_model": {
            "_": {
                "stem_name": {
                    "enum": ["Lead Vocal", "Drum Kit", "Kick", "Snare", "Risers", "Bass", "Backing Vocals", "Piano", "Electric Guitar", "Percussion", "String Section", "Synth", "Acoustic Guitar", "Sound Effects", "Synth Pad", "Synth Bass", "Guitar", "Brass Section", "Organ", "Electronic Drum Kit", "Lead Electric Guitar", "Synth Keys", "Rhythm Electric Guitar", "Electric Piano", "Upright Bass", "Keyboards", "Distorted Electric Guitar", "Synth Strings", "Synth Lead", "Woodwinds", "Rhythm Acoustic Guitar", "Flute", "Harp", "Tambourine", "Trumpet", "Arpeggiator", "Accordion", "Fiddle", "Pedal Steel Guitar", "Synth Voice", "Violin", "Digital Piano", "Synth Brass", "Mandolin", "Choir", "Banjo", "Bells", "Clarinet", "Tenor Saxophone", "Trombone", "Shaker", "French Horn", "Glockenspiel", "Electric Bass", "Cello", "Timpani", "Harmonica", "Marimba", "Vibraphone", "Lap Steel Guitar", "Saxophone", "Orchestra", "Horns", "Cymbals", "Hand Clap", "Oboe", "Celesta", "Congas", "Drone", "Alto Saxophone", "Double Bass", "Ukulele", "Harpsichord", "Baritone Saxophone", "Xylophone", "Tuba", "Bass Guitar", "Whistle", "Lead Guitar", "Rhodes", "808", "Bongos", "Bassoon", "Cowbell", "Viola", "Sitar", "Steel Drums", "Piccolo", "Theremin", "Bagpipes", "Hi-Hat", "Music Box", "Melodica", "Tabla", "Koto", "Djembe", "Taiko", "Didgeridoo"]
                },
                "type": {
                    "enum": ["separate_vocal", "split_stem", "split_stem_advanced"]
                }
            }
        }
    },
    "suno/stitch-audio": {
        "models": ["suno-v4", "suno-v4.5", "suno-v4.5-plus", "suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v4": {},
            "suno-v4.5": {},
            "suno-v4.5-plus": {},
            "suno-v5": {},
            "suno-v5.5": {}
        }
    },
    "suno/text-to-music": {
        "models": ["suno-v4", "suno-v4.5", "suno-v4.5-all", "suno-v4.5-plus", "suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v4": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v4.5": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v4.5-all": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v4.5-plus": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v5": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            },
            "suno-v5.5": {
                "persona_type": {
                    "enum": ["style", "voice"]
                },
                "vocal_gender": {
                    "enum": ["male", "female"]
                },
                "vocal_mode": {
                    "enum": ["auto_lyrics", "exact_lyrics", "instrumental"]
                }
            }
        }
    },
    "suno/text-to-sound": {
        "models": ["suno-v5", "suno-v5.5"],
        "fields_by_model": {
            "suno-v5": {
                "sound_key": {
                    "enum": ["Cm", "C#m", "Dm", "D#m", "Em", "Fm", "F#m", "Gm", "G#m", "Am", "A#m", "Bm", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
                }
            },
            "suno-v5.5": {
                "sound_key": {
                    "enum": ["Cm", "C#m", "Dm", "D#m", "Em", "Fm", "F#m", "Gm", "G#m", "Am", "A#m", "Bm", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
                }
            }
        }
    },
    "suno/visualize-music": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "suno/voice-to-validation-phrase": {
        "models": [],
        "fields_by_model": {
            "_": {
                "language": {
                    "enum": ["en", "zh", "es", "fr", "pt", "de", "ja", "ko", "hi", "ru"]
                }
            }
        }
    },
    "topaz/upscale-image": {
        "models": ["topaz-upscale-image"],
        "fields_by_model": {
            "topaz-upscale-image": {
                "upscale_factor": {
                    "enum": [1, 2, 4, 8]
                }
            }
        }
    },
    "topaz/upscale-video": {
        "models": ["topaz-upscale-video"],
        "fields_by_model": {
            "topaz-upscale-video": {
                "upscale_factor": {
                    "enum": [1, 2, 4]
                }
            }
        }
    },
    "veo-3-1/extend-video": {
        "models": [],
        "fields_by_model": {
            "_": {}
        }
    },
    "veo-3-1/text-to-video": {
        "models": ["veo-3.1", "veo-3.1-fast", "veo-3.1-lite"],
        "fields_by_model": {
            "veo-3.1": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "auto"]
                },
                "duration_seconds": {
                    "enum": [4, 6, 8]
                },
                "input_mode": {
                    "enum": ["text", "first_and_last_frames", "reference"]
                }
            },
            "veo-3.1-fast": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "auto"]
                },
                "duration_seconds": {
                    "enum": [4, 6, 8]
                },
                "input_mode": {
                    "enum": ["text", "first_and_last_frames", "reference"]
                }
            },
            "veo-3.1-lite": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16"]
                },
                "duration_seconds": {
                    "enum": [4, 6, 8]
                },
                "input_mode": {
                    "enum": ["text", "first_and_last_frames", "reference"]
                }
            }
        }
    },
    "veo-3-1/upscale-video": {
        "models": [],
        "fields_by_model": {
            "_": {
                "output_resolution": {
                    "enum": ["1080p", "4k"]
                }
            }
        }
    },
    "volcengine-lip-sync/lip-sync-video": {
        "models": ["volcengine-lip-sync"],
        "fields_by_model": {
            "volcengine-lip-sync": {
                "mode": {
                    "enum": ["lite", "basic"]
                }
            }
        }
    },
    "wan/animate": {
        "models": ["wan-2.2-animate-move", "wan-2.2-animate-replace"],
        "fields_by_model": {
            "wan-2.2-animate-move": {
                "output_resolution": {
                    "enum": ["480p", "580p", "720p"]
                }
            },
            "wan-2.2-animate-replace": {
                "output_resolution": {
                    "enum": ["480p", "580p", "720p"]
                }
            }
        }
    },
    "wan/edit-video": {
        "models": ["wan-2.6-edit-video", "wan-2.6-flash-edit-video", "wan-2.7-edit-video"],
        "fields_by_model": {
            "wan-2.6-edit-video": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "wan-2.6-flash-edit-video": {},
            "wan-2.7-edit-video": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "wan/image-to-video": {
        "models": ["wan-2.2-a14b-image-to-video-turbo", "wan-2.5-image-to-video", "wan-2.6-flash-image-to-video", "wan-2.6-image-to-video", "wan-2.7-image-to-video"],
        "fields_by_model": {
            "wan-2.2-a14b-image-to-video-turbo": {
                "output_resolution": {
                    "enum": ["480p", "720p"]
                }
            },
            "wan-2.5-image-to-video": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "wan-2.6-flash-image-to-video": {
                "duration_seconds": {
                    "enum": [5, 10, 15]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "wan-2.6-image-to-video": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "wan-2.7-image-to-video": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "wan/speech-to-video": {
        "models": ["wan-2.2-a14b-speech-to-video-turbo"],
        "fields_by_model": {
            "wan-2.2-a14b-speech-to-video-turbo": {
                "output_resolution": {
                    "enum": ["480p", "580p", "720p"]
                }
            }
        }
    },
    "wan/text-to-image": {
        "models": ["wan-2.7-image", "wan-2.7-image-pro"],
        "fields_by_model": {
            "wan-2.7-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "16:9", "4:3", "21:9", "3:4", "9:16", "8:1", "1:8"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k", "4k"]
                }
            },
            "wan-2.7-image-pro": {
                "aspect_ratio": {
                    "enum": ["1:1", "16:9", "4:3", "21:9", "3:4", "9:16", "8:1", "1:8"]
                },
                "output_resolution": {
                    "enum": ["1k", "2k", "4k"]
                }
            }
        }
    },
    "wan/text-to-video": {
        "models": ["wan-2.2-a14b-text-to-video-turbo", "wan-2.5-text-to-video", "wan-2.6-text-to-video", "wan-2.7-r2v", "wan-2.7-text-to-video"],
        "fields_by_model": {
            "wan-2.2-a14b-text-to-video-turbo": {
                "output_resolution": {
                    "enum": ["480p", "580p", "720p"]
                }
            },
            "wan-2.5-text-to-video": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "wan-2.6-text-to-video": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "wan-2.7-r2v": {
                "aspect_ratio": {
                    "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"]
                },
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            },
            "wan-2.7-text-to-video": {
                "output_resolution": {
                    "enum": ["720p", "1080p"]
                }
            }
        }
    },
    "z-image/text-to-image": {
        "models": ["z-image"],
        "fields_by_model": {
            "z-image": {
                "aspect_ratio": {
                    "enum": ["1:1", "4:3", "3:4", "16:9", "9:16"]
                }
            }
        }
    }
}
