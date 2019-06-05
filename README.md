# YDWeb: Console-Based Youdao Dictionary

`ydweb` is a console-based dictionary with contents crawled from the youdao website. No APIs are required.

## To-Do List

- [x] Basic dictionary search.
- [x] Verbose levels with exclamation marks `!`.
- [x] Cache crawled contents.
- [x] Search and cache wordlist in parallel.
- [x] Offline dictionaries.

## Dependencies

`YDWeb` depends on the following python packages:

* `requests`
* `pyquery`
* `prompt_toolkit`

## Usage

Simple search:

```
> raccoon                                                                       
raccoon
英 [rə'kuːn] 美 [ræ'kun]
n. 浣熊；浣熊毛皮
[ 复数 raccoons或raccoon ]
```

Increase verbose level with `!`. Single exclamation:

```
> raccoon!
raccoon
英 [rə'kuːn] 美 [ræ'kun]
n. 浣熊；浣熊毛皮
[ 复数 raccoons或raccoon ]

柯林斯英汉双解大词典
raccoon /rəˈkuːn/ (also racoon) ( raccoon )
1.
N-COUNT A raccoon is a small animal that has dark-coloured fur with white stripes on its face and on its long tail. Raccoons live in forests in North and Central America. 浣熊
```

Double exclamation:

```
> raccoon!!
raccoon
英 [rə'kuːn] 美 [ræ'kun]
n. 浣熊；浣熊毛皮
[ 复数 raccoons或raccoon ]

柯林斯英汉双解大词典
raccoon /rəˈkuːn/ (also racoon) ( raccoon )
1.
N-COUNT A raccoon is a small animal that has dark-coloured fur with white stripes on its face and on its long tail. Raccoons live in forests in North and Central America. 浣熊

同近义词
n. 浣熊；浣熊毛皮
racoon , coon
```

Triple exclamations:

```
> raccoon!!!
raccoon
英 [rə'kuːn] 美 [ræ'kun]
n. 浣熊；浣熊毛皮
[ 复数 raccoons或raccoon ]

柯林斯英汉双解大词典
raccoon /rəˈkuːn/ (also racoon) ( raccoon )
1.
N-COUNT A raccoon is a small animal that has dark-coloured fur with white stripes on its face and on its long tail. Raccoons live in forests in North and Central America. 浣熊

同近义词
n. 浣熊；浣熊毛皮
racoon , coon

双语例句权威例句
If you domesticate this raccoon, it will have trouble living in the wild.
如果你驯养这只浣熊，它生活在野外将会有困难。
m.dict.cn
“My best friends are the woodchuck and the porcupine and the raccoon, not because I like them, but because I know what they’re capable of, ” Mr. King said.
金先生说：“我最好的朋友就是土拨鼠、豪猪还有浣熊，不是因为我喜欢它们，而是因为我晓得它们有什么本事。
article.yeeyan.org
The dog chased the raccoon up a tree.
这只狗把浣熊追赶到了树上。
http://dj.iciba.com
更多双语例句
Upon his return, he saw where the raccoon had done some apparent last-minute thrashing.
NEWYORKER: Tenth of December
You can also become marksman Rocket Raccoon or Squirrel Girl and, um, talk to squirrels.
FORBES: A First Look at the Upcoming MMO 'Marvel Heroes'
```

