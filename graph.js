// Import from "@langchain/langgraph/web"
import {
    END,
    START,
    StateGraph,
    Annotation,
} from "@langchain/langgraph/web";
import { BaseMessage, HumanMessage } from "@langchain/core/messages";

export async function initializeLangGraphWorkflow() {
    // Define the root state with annotations
    const GraphState = Annotation.Root({
        messages: Annotation({
            reducer: (x, y) => x.concat(y),
        }),
    });

    // Define the function for the graph node
    const nodeFn = async (_state) => {
        return { messages: [new HumanMessage("Hello from the browser!")] };
    };

    // Create the graph
    const workflow = new StateGraph(GraphState)
        .addNode("node", nodeFn)
        .addEdge(START, "node")
        .addEdge("node", END);

    // Compile the workflow
    const compiledWorkflow = workflow.compile({});

    console.log(compiledWorkflow);

    return compiledWorkflow;
}

// Function to run the workflow and get the final state
export async function runLangGraphWorkflow() {
    const workflow = await initializeLangGraphWorkflow();
    const finalState = await workflow.invoke({ messages: [] });
    return finalState.messages[finalState.messages.length - 1].content;
}
