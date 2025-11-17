# First Nanochat run

To get my feed wet with [Andrej Karpathy's Nanochat](https://github.com/karpathy/nanochat), I did a [first run on my Mac Mini](https://github.com/maluio/nanochat-wrapper/tree/main/runs/01-mac-mini).

WHat is Nanochat? From their docs:

> This repo [Nanochat] is a full-stack implementation of an LLM like ChatGPT in a single, clean, minimal, hackable, dependency-lite codebase. nanochat is designed to run on a single 8XH100 node via scripts like speedrun.sh, that run the entire pipeline start to end. This includes tokenization, pretraining, finetuning, evaluation, inference, and web serving over a simple UI so that you can talk to your own LLM just like ChatGPT. nanochat will become the capstone project of the course LLM101n being developed by Eureka Labs.

To get a somewhat GPT there is a `speedrun` that costs ~100 USD. I decided to get familiar with how it works first. Thankfully, it's easy to tweak Nanochat's hyperparameters and to even run it on a CPU if you don't have CUDA hardware available.

I changed the hyperparams until I got a full run including training the tokenzier, pre-training, mid-training and supervised fine-tuning.

You end up with a working model that generates sound language but that doesn't make a whole lot of sense:

```bash
python -m scripts.chat_cli -p "Why is the sky blue?"

[...]

Assistant: This means that the time, we need to the bank, and the next the total of the first.

This can be a states and a more comprehensive understanding of 3.

One of the next with the top of two distinct, the number of the sum of the next and 3. This can be a point to the equation in a manual approach between these skills, which is we need to be a clear:
1 = 3, and make the sentence! + 2^3, the convention has not interested in the number of the equation, the next can be a total is an example, and the first, and we can be 3, we can be a more concise that the number of the string.


3 + 3 + 3y), which is a second.<|assistant_end|>
```
