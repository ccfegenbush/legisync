import { WebTracerProvider } from "@opentelemetry/sdk-trace-web";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { SimpleSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { ZoneContextManager } from "@opentelemetry/context-zone";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { DocumentLoadInstrumentation } from "@opentelemetry/instrumentation-document-load";
import { UserInteractionInstrumentation } from "@opentelemetry/instrumentation-user-interaction";
import { FetchInstrumentation } from "@opentelemetry/instrumentation-fetch";

export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") return;
  const provider = new WebTracerProvider({
    spanProcessors: [
      new SimpleSpanProcessor(
        new OTLPTraceExporter({
          url: "http://localhost:4318/v1/traces", // Replace with your Grafana Cloud or Jaeger endpoint
        })
      ),
    ],
  });
  provider.register({ contextManager: new ZoneContextManager() });
  registerInstrumentations({
    instrumentations: [
      new DocumentLoadInstrumentation(),
      new UserInteractionInstrumentation(),
      new FetchInstrumentation(),
    ],
  });
}
