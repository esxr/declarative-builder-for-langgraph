import { runLangGraphWorkflow } from './graph.js'

async function main() {
    const result = await runLangGraphWorkflow();
    console.log(result);
}

main();
