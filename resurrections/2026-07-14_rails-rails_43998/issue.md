# Rails cashes with Ruby 3.1.0 release

**Repository:** [rails/rails](https://github.com/rails/rails)
**Issue:** [rails/rails#43998](https://github.com/rails/rails/issues/43998)
**Reactions:** 86 👍
**Created:** 2021-12-25T20:49:26Z
**Last Activity:** 2022-01-08T20:53:39Z
**Labels:** 

---

## Original Description

### Steps to reproduce

```ruby
ruby -v
# => ruby 3.1.0p0 (2021-12-25 revision fb4df44d16) [arm64-darwin21]

rails new test-app
cd test-app
rails s
```

### Expected behavior
Create a new rails app and serve it.

### Actual behavior
Crashes during the project creation process:
```bash
...
         run  bundle binstubs bundler
       rails  importmap:install
Calling `DidYouMean::SPELL_CHECKERS.merge!(error_name => spell_checker)' has been deprecated. Please call `DidYouMean.correct_error(error_name, spell_checker)' instead.
rails aborted!
Rails::Engine is abstract, you cannot instantiate it directly.
/Users/erik/Code/test-app/config/application.rb:3:in `<main>'
/Users/erik/Code/test-app/Rakefile:4:in `<main>'
bin/rails:4:in `<main>'
...
```

Furthermore, `test-app` gets generated, but cannot be served:
```bash
Calling `DidYouMean::SPELL_CHECKERS.merge!(error_name => spell_checker)' has been deprecated. Please call `DidYouMean.correct_error(error_name, spell_checker)' instead.
[WARNING] Could not load command "rails/commands/server/server_command". Error: Rails::Engine is abstract, you cannot instantiate it directly..
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/railties-7.0.0/lib/rails/railtie.rb:246:in `initialize'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/railties-7.0.0/lib/rails/railtie.rb:184:in `new'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/railties-7.0.0/lib/rails/railtie.rb:184:in `instance'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/railties-7.0.0/lib/rails/railtie.rb:223:in `method_missing'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/activesupport-7.0.0/lib/active_support/descendants_tracker.rb:90:in `descendants'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/activesupport-7.0.0/lib/active_support/callbacks.rb:923:in `block in define_callbacks'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/activesupport-7.0.0/lib/active_support/callbacks.rb:920:in `each'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/activesupport-7.0.0/lib/active_support/callbacks.rb:920:in `define_callbacks'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/railties-7.0.0/lib/rails/engine.rb:427:in `<class:Engine>'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/railties-7.0.0/lib/rails/engine.rb:349:in `<module:Rails>'
/Users/erik/.rbenv/versions/3.1.0/lib/ruby/gems/3.1.0/gems/railties-7.0.0/lib/rails/engine.rb:11:in `<main>'
... 
```

### System configuration
**Rails version**: 7.0.0

**Ruby version**: ruby 3.1.0p0 (2021-12-25 revision fb4df44d16) [arm64-darwin21]


---

*Resurrected by Resurrection Bot 🧬*
