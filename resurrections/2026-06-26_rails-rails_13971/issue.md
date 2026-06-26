# ActiveRecord enum: use validation if exists instead of raising ArgumentError

**Repository:** [rails/rails](https://github.com/rails/rails)
**Issue:** [rails/rails#13971](https://github.com/rails/rails/issues/13971)
**Reactions:** 98 👍
**Created:** 2014-02-07T22:48:04Z
**Last Activity:** 2023-09-03T23:42:29Z
**Labels:** activerecord, enum

---

## Original Description

Regarding [ActiveRecord::Enum](http://edgeapi.rubyonrails.org/classes/ActiveRecord/Enum.html), assume you had something like

``` ruby
class Project < ActiveRecord::Base
  enum color: [:blue, :green, :red]
  validates :color, inclusion: { in: [:blue, :green, :red] }
end
```

Currently, if a "bad" value (say, "orange") is passed in, [an `ArgumentError` is raised](https://github.com/amrnt/rails/blob/b8302bcfdaec2a9e7658262d6feeb535c572922d/activerecord/lib/active_record/enum.rb#L87).

It would be nice if the validation was preferred (with the `ArgumentError` as a fallback if there was no validation on that attribute) so that you'd be able to return a nicer error on the object later via the standard means:

``` ruby
object.errors.messages
# => {:color=>["is not included in the list"]} kind of thing
```


---

*Resurrected by Resurrection Bot 🧬*
