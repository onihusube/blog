# ［Meson］Meson for C++の苦闘記

### 基本



```meson
project('test', 'cpp')

executable('test_exe', `test.cpp`)
```

### 参考文献
- [CMakeの代替 (となってほしい)、Mesonチュートリアル - Qita](https://qiita.com/turenar/items/c727834fbf701beb47ef)
- [Reference manual - The Meson Build System](https://mesonbuild.com/Reference-manual.html)