package ai.runapi.core.contract;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import ai.runapi.core.errors.ValidationException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;

/** Rule messages must match every other SDK (sdk/contract_rule_messages.json). */
class ContractRuleMessagesTest {
  private static final Path FIXTURE = Paths.get("..", "..", "contract_rule_messages.json");

  @TestFactory
  Stream<DynamicTest> matchesSharedFixture() throws IOException {
    // The shared fixture lives in the SDK monorepo; the public package repo does not ship it.
    assumeTrue(Files.exists(FIXTURE), "shared SDK fixture not available");

    ObjectMapper mapper = new ObjectMapper();
    List<DynamicTest> tests = new ArrayList<DynamicTest>();
    for (JsonNode sharedCase : mapper.readTree(FIXTURE.toFile()).get("cases")) {
      String action = sharedCase.get("action").asText();
      String message = sharedCase.get("message").asText();
      Map<String, Object> params =
          mapper.convertValue(sharedCase.get("params"), new TypeReference<Map<String, Object>>() {});
      tests.add(
          DynamicTest.dynamicTest(
              sharedCase.get("name").asText(),
              () -> {
                ValidationException error =
                    assertThrows(ValidationException.class, () -> ContractValidator.validate(action, params));
                assertEquals(message, error.getMessage());
              }));
    }
    return tests.stream();
  }
}
