plugins {
  `java-platform`
  `maven-publish`
}

description = "Bill of materials for aligning RunAPI Java SDK artifact versions."

javaPlatform {
  allowDependencies()
}

dependencies {
  constraints {
    api("ai.runapi:runapi-core:0.6.0")
    api("ai.runapi:runapi-elevenlabs:0.1.1")
    api("ai.runapi:runapi-flux-kontext:0.1.1")
    api("ai.runapi:runapi-flux-2:0.2.0")
    api("ai.runapi:runapi-flux:0.1.0")
    api("ai.runapi:runapi-gpt-image:0.1.1")
    api("ai.runapi:runapi-gpt-image-2:0.1.1")
    api("ai.runapi:runapi-gpt-4o-image:0.1.1")
    api("ai.runapi:runapi-grok-imagine:0.1.5")
    api("ai.runapi:runapi-hailuo:0.1.1")
    api("ai.runapi:runapi-minimax-h3:0.1.0")
    api("ai.runapi:runapi-happyhorse:0.1.1")
    api("ai.runapi:runapi-pixverse:0.1.1")
    api("ai.runapi:runapi-ideogram-v3:0.1.1")
    api("ai.runapi:runapi-imagen-4:0.1.2")
    api("ai.runapi:runapi-infinitetalk:0.1.1")
    api("ai.runapi:runapi-omnihuman:0.1.3")
    api("ai.runapi:runapi-gemini-omni:0.2.2")
    api("ai.runapi:runapi-openai-tts:0.1.1")
    api("ai.runapi:runapi-openai-transcription:0.1.0")
    api("ai.runapi:runapi-fish-audio:0.3.0")
    api("ai.runapi:runapi-gemini-tts:0.1.1")
    api("ai.runapi:runapi-kling:0.1.6")
    api("ai.runapi:runapi-luma:0.1.1")
    api("ai.runapi:runapi-midjourney:0.3.0")
    api("ai.runapi:runapi-volcengine-lip-sync:0.1.1")
    api("ai.runapi:runapi-nano-banana:0.1.4")
    api("ai.runapi:runapi-qwen-2:0.1.1")
    api("ai.runapi:runapi-qwen-3:0.1.0")
    api("ai.runapi:runapi-qwen-image:0.1.0")
    api("ai.runapi:runapi-producer:0.2.0")
    api("ai.runapi:runapi-recraft:0.1.1")
    api("ai.runapi:runapi-runway:0.1.1")
    api("ai.runapi:runapi-runway-aleph:0.1.1")
    api("ai.runapi:runapi-seedance:0.1.6")
    api("ai.runapi:runapi-seedream:0.1.3")
    api("ai.runapi:runapi-suno:0.3.1")
    api("ai.runapi:runapi-topaz:0.1.1")
    api("ai.runapi:runapi-veo-3.1:0.1.2")
    api("ai.runapi:runapi-wan:0.1.3")
    api("ai.runapi:runapi-z-image:0.1.1")
  }
}

publishing {
  publications {
    create<MavenPublication>("mavenJava") {
      from(components["javaPlatform"])
      artifactId = "runapi-bom"
      pom {
        name = "RunAPI Java SDK BOM"
        description = "Bill of materials for RunAPI Java SDK artifacts."
        url = "https://runapi.ai/docs/resources/sdks"
        licenses {
          license {
            name = "Apache License, Version 2.0"
            url = "https://www.apache.org/licenses/LICENSE-2.0"
          }
        }
        developers {
          developer {
            id = "runapi"
            name = "RunAPI"
            email = "contact@runapi.ai"
          }
        }
        scm {
          url = "https://github.com/runapi-ai/core-sdk"
          connection = "scm:git:https://github.com/runapi-ai/core-sdk.git"
          developerConnection = "scm:git:ssh://git@github.com/runapi-ai/core-sdk.git"
        }
      }
    }
  }
}
